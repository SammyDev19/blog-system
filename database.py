import sqlite3
import os


class Database:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE_PATH = os.path.join(BASE_DIR, "blog.db")

        self.connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False
        )
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                UNIQUE(user_id, post_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)

        self.connection.commit()


    def add_user(self, username, password):
        self.cursor.execute("""
            SELECT COUNT(*) FROM users
        """)
        user_count = self.cursor.fetchone()[0]
        is_admin = 1 if user_count == 0 else 0
        self.cursor.execute("""
            INSERT INTO users (username, password, is_admin)
            VALUES (?, ?, ?)
        """, (username, password, is_admin))

        self.connection.commit()


    def get_user_by_username(self, username):

        self.cursor.execute("""
            SELECT * FROM users
            WHERE username = ?
        """, (username,))

        return self.cursor.fetchone()


    def get_posts(self):

        self.cursor.execute("""
            SELECT
                posts.id,
                posts.title,
                posts.content,
                posts.user_id,
                posts.created_at,
                users.username
            FROM posts
            JOIN users
            ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
        """)

        return self.cursor.fetchall()

    def add_post(self, title, content, user_id):

        self.cursor.execute("""
            INSERT INTO posts (title, content, user_id)
            VALUES (?, ?, ?)
        """, (title, content, user_id))

        self.connection.commit()


    def get_post(self, post_id):

        self.cursor.execute("""
            SELECT
                posts.id,
                posts.title,
                posts.content,
                posts.user_id,
                posts.created_at,
                users.username
            FROM posts
            JOIN users
            ON posts.user_id = users.id
            WHERE posts.id = ?
        """, (post_id,))

        return self.cursor.fetchone()


    def update_post(self, post_id, title, content):
        self.cursor.execute("""
            UPDATE posts
            SET title = ?, content = ?
            WHERE id = ?
        """, (title, content, post_id))

        self.connection.commit()


    def delete_post(self, post_id):

        self.cursor.execute("""
            DELETE FROM posts
            WHERE id = ?
        """, (post_id,))

        self.connection.commit()


    def add_comment(self, content, user_id, post_id):
        self.cursor.execute("""
            INSERT INTO comments (content, user_id, post_id)
            VALUES (?, ?, ?)
        """, (content, user_id, post_id))

        self.connection.commit()


    def get_comments(self, post_id):

        self.cursor.execute("""
            SELECT
                comments.id,
                comments.content,
                comments.user_id,
                comments.created_at,
                users.username
            FROM comments
            JOIN users
            ON comments.user_id = users.id
            WHERE comments.post_id = ?
            ORDER BY comments.created_at ASC
        """, (post_id,))

        return self.cursor.fetchall()


    def add_like(self, user_id, post_id):
        self.cursor.execute("""
            INSERT INTO likes (user_id, post_id)
            VALUES (?, ?)
        """, (user_id, post_id))

        self.connection.commit()


    def remove_like(self, user_id, post_id):

        self.cursor.execute("""
            DELETE FROM likes
            WHERE user_id = ? AND post_id = ?
        """, (user_id, post_id))

        self.connection.commit()


    def check_like(self, user_id, post_id):

        self.cursor.execute("""
            SELECT id FROM likes
            WHERE user_id = ? AND post_id = ?
        """, (user_id, post_id))

        return self.cursor.fetchone()


    def count_likes(self, post_id):

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM likes
            WHERE post_id = ?
        """, (post_id,))

        return self.cursor.fetchone()[0]


    def search_posts(self, query):
        self.cursor.execute("""
            SELECT
                posts.id,
                posts.title,
                posts.content,
                posts.user_id,
                posts.created_at,
                users.username
            FROM posts
            JOIN users
            ON posts.user_id = users.id
            WHERE posts.title LIKE ?
            OR posts.content LIKE ?
            ORDER BY posts.created_at DESC
        """, (f"%{query}%", f"%{query}%"))

        return self.cursor.fetchall()


    def delete_user(self, user_id):
        self.cursor.execute("""
            DELETE FROM likes
            WHERE user_id = ?
        """, (user_id,))

        self.cursor.execute("""
            DELETE FROM comments
            WHERE user_id = ?
        """, (user_id,))

        self.cursor.execute("""
            DELETE FROM posts
            WHERE user_id = ?
        """, (user_id,))

        self.cursor.execute("""
            DELETE FROM users
            WHERE id = ?
        """, (user_id,))

        self.connection.commit()


    def get_user_posts(self, user_id):
        self.cursor.execute("""
            SELECT id, title, content, created_at
            FROM posts
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))

        return self.cursor.fetchall()


    def get_users(self):
        self.cursor.execute("""
            SELECT id, username, is_admin
            FROM users
            ORDER BY id
        """)

        return self.cursor.fetchall()