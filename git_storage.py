import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GitStorage:
    """
    Git-based storage for tracking replied posts.
    Stores replied post IDs in a JSON file that's committed to the repository.
    """
    def __init__(self, storage_file='replied_posts.json'):
        self.storage_file = storage_file
        self.replied_posts = self._load_replied_posts()
    
    def _load_replied_posts(self):
        """Load replied posts from JSON file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} replied posts from {self.storage_file}")
                    return data
            except Exception as e:
                logger.error(f"Error loading replied posts: {e}")
                return {}
        else:
            logger.info(f"{self.storage_file} not found, starting fresh")
            return {}
    
    def _save_replied_posts(self):
        """Save replied posts to JSON file."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.replied_posts, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.replied_posts)} replied posts to {self.storage_file}")
        except Exception as e:
            logger.error(f"Error saving replied posts: {e}")
    
    def is_replied(self, post_id):
        """Check if a post has been replied to."""
        return post_id in self.replied_posts
    
    def mark_as_replied(self, post_id):
        """Mark a post as replied and save to file."""
        if post_id not in self.replied_posts:
            self.replied_posts[post_id] = datetime.now().isoformat()
            self._save_replied_posts()
            logger.info(f"Marked post {post_id} as replied")
