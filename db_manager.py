import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path='replied_posts.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS replied_posts (
                    post_id TEXT PRIMARY KEY,
                    replied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def is_replied(self, post_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM replied_posts WHERE post_id = ?', (post_id,))
            return cursor.fetchone() is not None

    def mark_as_replied(self, post_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO replied_posts (post_id) VALUES (?)', (post_id,))
            conn.commit()
