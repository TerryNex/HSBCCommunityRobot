import logging
import os

from dotenv import load_dotenv

from ai_handler import AIHandler
from git_storage import GitStorage
from forum_client import ForumClient
from utils import human_delay, logger

load_dotenv()

def main():
    logger.info("Starting Forum Reply Automator (6-Step Logic)...")

    # Initialize components
    storage = GitStorage()
    ai = AIHandler()

    forum_url = os.getenv("FORUM_BASE_URL")
    username = os.getenv("FORUM_USERNAME")
    password = os.getenv("FORUM_PASSWORD")
    
    # Parse ROOM_TITLES from environment variable
    room_titles_str = os.getenv("ROOM_TITLES", "Recent Subjects")
    if not room_titles_str or not room_titles_str.strip():
        allowed_room_titles = ["Recent Subjects"]
    else:
        allowed_room_titles = [title.strip() for title in room_titles_str.split(",") if title.strip()]
    logger.info(f"Allowed room titles: {allowed_room_titles}")

    client = ForumClient(forum_url, username, password)

    # 1. Validate Session
    if not client.validate_session():
        # 2. Login if expired
        if not client.login():
            logger.error("Authentication failed.")
            return

    # 3. Get Page Info
    page_info = client.get_page_info()
    if not page_info:
        logger.error("Failed to get page info.")
        return

    page_guid = page_info.get('pageGUID')

    # 4. Get Room Info (Priority: Recent Subjects)
    rooms = client.get_room_info(page_guid)
    if not rooms:
        logger.error("No rooms found.")
        return

    # Sort rooms for priority (Recent Subjects first)
    # Assuming "Recent Subjects" has a specific ID or title
    priority_rooms = sorted(rooms, key=lambda r: r.get('title') != "Recent Subjects")

    found_any_new_post = False

    for room in priority_rooms:
        room_guid = room['roomGUID']
        room_title = room['title']
        # Check if room title is in the allowed list from environment variable
        if room_title not in allowed_room_titles:
            logger.info(f"Skipping room: {room_title} ({room_guid})")
            continue
        logger.info(f"Checking room: {room_title} ({room_guid})")

        # 5. Get Conversations
        conversations = client.get_conversations(room_guid, page_guid)

        new_convos = [c for c in conversations if not storage.is_replied(c['conversationID'])]

        if not new_convos:
            logger.info(f"No new posts in room {room_title}. Moving to next...")
            continue

        found_any_new_post = True
        logger.info(f"Found {len(new_convos)} new posts in {room_title}.")
        for convo in new_convos:
            convo_id = convo['conversationID']
            content = convo.get('content', '')
            title = convo.get('title', 'No Title')
            username = convo.get('username', 'Unknown')

            logger.info(f"Processing post {convo_id}...")
            logger.info(f"   Title: {title}")
            logger.info(f"   Username: {username}")
            logger.info(f"   Message: {content}")

            # 6. Generate AI reply
            reply_content = ai.generate_reply(content, title)

            # test replay content
            logger.info(f"Generated reply: {reply_content}")
            if reply_content:
                # Human-like delay
                max_delay = int(os.getenv("RANDOM_DELAY_RANGE", 300))
                human_delay(max_delay)

                # 6. Submit reply and Like (Use specific room GUID from post if available)
                target_room_guid = convo.get('roomGUID', room_guid)
                if client.reply_and_like(target_room_guid, convo_id, reply_content):
                    storage.mark_as_replied(convo_id)
                    logger.info(f"Successfully processed post {convo_id}.")
                else:
                    logger.error(f"Failed to process post {convo_id}.")

            # If we replied to something in Recent Subjects, we might want to stop to avoid flooding
            # Or just continue based on user's preference.
            # The prompt said "In Recent Subjects can't find new post then go to other sections"
            # This implies if we find some, we process them.

    if not found_any_new_post:
        logger.info("Checked all rooms, no new posts found.")

    logger.info("Automator run completed.")

if __name__ == "__main__":
    main()
