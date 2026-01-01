import pytest
import os
from forum_client import ForumClient
from ai_handler import AIHandler
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def forum_client():
    url = os.getenv("FORUM_BASE_URL")
    user = os.getenv("FORUM_USERNAME")
    pw = os.getenv("FORUM_PASSWORD")
    return ForumClient(url, user, pw)

@pytest.fixture
def ai_handler():
    return AIHandler()

def test_perplexity_api(ai_handler):
    """Test Perplexity AI response generation."""
    test_content = "如何評價 2024 年的科技發展？"
    reply = ai_handler.generate_reply(test_content)
    assert reply is not None
    assert len(reply) > 0
    print(f"\nPerplexity Reply: {reply}")

def test_step1_validate_session(forum_client):
    """Step 1: Validate token status."""
    # Mock behavior: return True if we want to bypass login or False if we want to trigger it.
    # For testing the logic, we expect it to return True eventually.
    assert forum_client.validate_session() is True

def test_step2_login(forum_client):
    """Step 2: Login and refresh token."""
    # Ensure it works
    assert forum_client.login() is True
    assert forum_client.token is not None

def test_step3_get_page_guid(forum_client):
    """Step 3: Get page info."""
    forum_client.login() # Ensure logged in
    info = forum_client.get_page_info()
    assert info is not None
    assert "pageGUID" in info

def test_step4_get_room_guid(forum_client):
    """Step 4: Get room IDs and stats."""
    forum_client.login()
    page_guid = "page_001"
    rooms = forum_client.get_room_info(page_guid)
    assert isinstance(rooms, list)
    assert len(rooms) > 0
    assert "roomGUID" in rooms[0]

def test_step5_get_conversation_id(forum_client):
    """Step 5: Get conversation IDs (post IDs)."""
    forum_client.login()
    room_guid = "room_recent"
    convos = forum_client.get_conversations(room_guid)
    assert isinstance(convos, list)
    assert len(convos) > 0
    assert "conversationID" in convos[0]

def test_step6_reply_and_like(forum_client):
    """Step 6: Reply and like."""
    forum_client.login()
    assert forum_client.reply_and_like("room_recent", "convo_101", "測試回覆內容") is True
