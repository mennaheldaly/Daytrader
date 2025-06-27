import sqlite3
import hashlib

class UserManager:
    def __init__(self, db_path='users.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_user_table()

    def create_user_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, email, password):
        password_hash = self.hash_password(password)
        try:
            with self.conn:
                self.conn.execute(
                    'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                    (username, email, password_hash)
                )
            return True, 'Registration successful.'
        except sqlite3.IntegrityError as e:
            return False, f'Error: {str(e)}'

    def authenticate_user(self, username, password):
        password_hash = self.hash_password(password)
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM users WHERE username=? AND password_hash=?', (username, password_hash))
        user = cur.fetchone()
        return user is not None

    def get_user_info(self, username):
        cur = self.conn.cursor()
        cur.execute('SELECT id, username, email FROM users WHERE username=?', (username,))
        return cur.fetchone() 