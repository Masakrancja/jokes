import hashlib
from flask import session
class Auth:
    def __init__(self, conn):
        self.conn = conn

    def get_user_id:
        if 'user_id' in session:
            return session['user_id']
        return None

    def check_user(self, login, password):
        pass

    def insert_user(self, login, hash_password):
        pass


