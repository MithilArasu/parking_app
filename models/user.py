from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import g

def get_db():
    from app import get_db
    return get_db()

class User(UserMixin):
    def __init__(self, row):
        self.id = row['id']
        self.username = row['username']
        self.password = row['password']
        self.is_admin = bool(row['is_admin'])

    @staticmethod
    def get(user_id):
        db = get_db()
        row = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        return User(row) if row else None

    @staticmethod
    def get_by_username(username):
        db = get_db()
        row = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        return User(row) if row else None

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def get_all_non_admin():
        db = get_db()
        rows = db.execute('SELECT * FROM users WHERE is_admin=0').fetchall()
        return [User(row) for row in rows]
