import json
import logging

import requests

from config_manager import ConfigManager
from utils import get_random_headers

logger = logging.getLogger(__name__)

class ForumClient:
    """
    Implements the real 6-step forum interaction logic for HSBC Community (Square Community).
    """
    def __init__(self, base_url, username, password):
        # Note: base_url is split between query and command in reality, but we can store the common part or just hardcode endpoints.
        self.query_url = "https://serviceapi-query.square-community.com.au"
        self.command_url = "https://serviceapi-command.square-community.com.au"
        self.origin = "https://hsbccommunityhk.square-community.com.au"

        self.username = username
        self.password = password
        self.config = ConfigManager()
        self.session = requests.Session()

        # Base headers used across requests
        self.session.headers.update({
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'origin': self.origin,
            'referer': f"{self.origin}/"
        })

        # Load token if exists
        self.token = self.config.get("auth_token")
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def validate_session(self):
        """Step 1: Validate Login Status."""
        logger.info("Step 1: Validating token status...")
        # Fixed PageGuid for validation check as per docs
        page_guid = "ca6305b6-d6cd-4940-a4d8-dc54d2f66050"
        url = f"{self.query_url}/PageService/AllowedToNavigateToPage?pageGuid={page_guid}"

        try:
            response = self.session.get(url)
            if response.status_code == 200:
                logger.info("Session is valid.")
                return True
            logger.warning(f"Session invalid (Status: {response.status_code}).")
            return False
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False

    def login(self):
        """Step 2: Login / Refresh Token."""
        logger.info("Step 2: Logging in...")
        url = f"{self.command_url}/AuthorizationService/ParticipantLogin"

        # Specific headers for login
        # headers = {
        #     'squareguid': "bef72afd-098a-427f-a0a8-298af4aba1af",
        #     'clientguid': "9b579d63-9a66-4685-9c43-f665a790a3fb",
        #     'Content-Type': "application/json"
        # }
        headers = {
          'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
          'origin': "https://hsbccommunityhk.square-community.com.au"
        }
        self.session.headers.update(headers)

        payload = {
            'username': self.username,
            'password': self.password,
            'change': "undefined"
        }

        try:
            response = self.session.post(url, data=payload)
            response.raise_for_status()

            # Response is plain text token
            self.token = response.text

            # Save and update session
            self.config.set("auth_token", self.token)
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            logger.info("Login successful. Token refreshed.")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def get_page_info(self):
        """Step 3: Get Page GUID (Target: '傾下講下')."""
        logger.info("Step 3: Fetching Page Info...")
        url = f"{self.query_url}/PageService/ListPageConsumer"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            target_name = "傾下講下"
            for page in data.get("List", []):
                if page.get("Name") == target_name:
                    logger.info(f"Found page '{target_name}' with GUID: {page['Guid']}")
                    return {"pageGUID": page['Guid']}

            logger.error(f"Page '{target_name}' not found.")
            return None
        except Exception as e:
            logger.error(f"Get page info failed: {e}")
            return None

    def get_room_info(self, page_guid):
        """Step 4: Get Room GUIDs."""
        logger.info(f"Step 4: Fetching Room Info for page {page_guid}...")
        url = f"{self.command_url}/ForumService/GetForumRooms"

        try:
            response = self.session.post(url, json={"guid": page_guid})
            response.raise_for_status()
            data = response.json()

            rooms = []

            # Explicitly add "Recent Subjects" (Virtual Room with Update ID)
            rooms.append({
                "roomGUID": "00000000-0000-0000-0000-000000000000",
                "title": "Recent Subjects",
                "topicCount": 0 # Unknown, but priority
            })

            for room in data.get("Rooms", []):
                if room.get("IsVisible"):
                    rooms.append({
                        "roomGUID": room["Guid"],
                        "title": room["Name"],
                        "topicCount": room.get("ConversationsCount", 0)
                    })
            return rooms
        except Exception as e:
            logger.error(f"Get room info failed: {e}")
            return []

    def get_conversations(self, room_guid, page_guid="bc7de0d9-cce3-4019-b7a9-ad8f843f320d"):
        """Step 5: Get Conversations in Room."""
        logger.info(f"Step 5: Fetching conversations for room {room_guid}...")
        url = f"{self.command_url}/ForumService/GetConversationsInRoom"

        payload = {
            "pageGuid": page_guid,
            "roomGuid": room_guid,
            "pageNumber": 1,
            "limit": 1
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            conversations = []
            for item in data.get("Items", []):
                conversations.append({
                    "conversationID": item["Guid"], # Used as Guid/ParentMessageGuid
                    "roomGUID": item.get("RoomGuid"), # Specific room GUID for reply
                    "content": item.get("Message", "") or item.get("Title", ""),
                    "title": item.get("Title", ""),
                    "isLiked": item.get("IsLiked", False)
                })
            return conversations
        except Exception as e:
            logger.error(f"Get conversations failed: {e}")
            return []

    def reply_and_like(self, room_guid, post_guid, message):
        """Step 6 & 7: Reply to conversation and Like the new reply."""
        logger.info(f"Step 6: Replying to post {post_guid}...")
        url_reply = f"{self.command_url}/ConversationService/ReplyToConversation"

        # Construct specific JSON string for 'request' field
        inner_request = {
            "Room": room_guid,
            "Guid": post_guid,
            "ParentMessageGuid": post_guid,
            "Message": message,
            "Type": 4,
            "Stimuli": [],
            "Attachments": []
        }

        # Use files format for multipart/form-data submission
        # The tuple format is: (filename, content)
        # When filename=None, it creates a plain form field (not a file upload)
        files = {
            "request": (
                None,
                json.dumps(inner_request, separators=(',', ':'), ensure_ascii=False)
            )
        }

        try:
            # 1. Reply using self.session
            response = self.session.post(url_reply, files=files)
            response.raise_for_status()
            
            # Response is the new Conversation GUID (string)
            new_reply_guid = response.text.replace('"', '')
            logger.info(f"Reply successful. New GUID: {new_reply_guid}")
            
            # 2. Like (Step 7)
            logger.info(f"Step 7: Liking the new reply {new_reply_guid}...")
            url_like = f"{self.command_url}/ConversationService/LikeConversation"
            like_payload = {"ConversationGuid": new_reply_guid}
            
            # Use self.session for Like request as well
            _like_response = self.session.post(url_like, json=like_payload)
            _like_response.raise_for_status()
            logger.info("Like successful.")

            return True
        except Exception as e:
            logger.error(f"Reply/Like failed: {e}")
            return False
