import logging
import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

from ai_handler import AIHandler
from git_storage import GitStorage
from forum_client import ForumClient
from utils import human_delay, logger, is_within_hours, HK_TIMEZONE

load_dotenv()


def is_post_within_hours(date_posted_str, hours_filter):
    """
    Check if a post was posted within the last X hours.
    Uses shared utility function for date parsing.
    
    Args:
        date_posted_str: ISO 8601 timestamp e.g. "2026-01-07T15:04:51.870Z"
        hours_filter: Number of hours to look back
        
    Returns:
        True if post is within the time window, False otherwise
    """
    if not date_posted_str or not hours_filter:
        return True  # If no date or filter, consider it valid
    
    result = is_within_hours(date_posted_str, hours_filter)
    logger.debug(f"Post date: {date_posted_str}, within {hours_filter}h: {result}")
    return result

def main():
    logger.info("Starting Forum Reply Automator (6-Step Logic)...")

    # Initialize components
    storage = GitStorage()
    ai = AIHandler()

    forum_url = os.getenv("FORUM_BASE_URL")
    username = os.getenv("FORUM_USERNAME")
    password = os.getenv("FORUM_PASSWORD")
    
    # Parse ROOM_TITLES from environment variable
    # Default to the 6 new room titles instead of "Recent Subjects"
    default_rooms = "精明消費,理財有道,環球智庫,加點保障,靈活信貸,其他"
    room_titles_str = os.getenv("ROOM_TITLES", default_rooms)
    if not room_titles_str or not room_titles_str.strip():
        allowed_room_titles = [title.strip() for title in default_rooms.split(",")]
    else:
        allowed_room_titles = [title.strip() for title in room_titles_str.split(",") if title.strip()]
    logger.info(f"Allowed room titles: {allowed_room_titles}")
    
    # Parse HOURS_FILTER from environment variable (optional)
    hours_filter = None
    hours_filter_str = os.getenv("HOURS_FILTER", "")
    if hours_filter_str and hours_filter_str.strip():
        try:
            hours_filter = int(hours_filter_str.strip())
            if hours_filter <= 0:
                logger.warning(f"HOURS_FILTER must be positive, ignoring: {hours_filter}")
                hours_filter = None
            else:
                logger.info(f"Using time-based filtering: only posts within last {hours_filter} hours")
        except ValueError:
            logger.warning(f"Invalid HOURS_FILTER value '{hours_filter_str}', ignoring")
            hours_filter = None

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

    # 4. Get Room Info
    rooms = client.get_room_info(page_guid)
    if not rooms:
        logger.error("No rooms found.")
        return

    # Sort rooms alphabetically by title (no special priority)
    priority_rooms = sorted(rooms, key=lambda r: r.get('title', ''))

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

        # Filter posts based on HOURS_FILTER (time-based) or replied status
        if hours_filter:
            # Time-based filtering: only posts within the last X hours
            new_convos = [c for c in conversations 
                         if is_post_within_hours(c.get('datePosted', ''), hours_filter)
                         and not storage.is_replied(c['conversationID'])]
            logger.info(f"Filtered to {len(new_convos)} posts within last {hours_filter} hours (and not replied)")
        else:
            # Traditional filtering: only posts not yet replied to
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
            date_posted = convo.get('datePosted', 'Unknown')

            logger.info(f"Processing post {convo_id}...")
            logger.info(f"   Title: {title}")
            logger.info(f"   Username: {username}")
            logger.info(f"   Posted: {date_posted}")
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

            # Continue processing all matched posts

    if not found_any_new_post:
        logger.info("Checked all rooms, no new posts found.")

    logger.info("Automator run completed.")

if __name__ == "__main__":
    main()
