import hashlib, re, datetime
import sqlite3
from flask import abort

from flask import session
class Auth:
    def __init__(self, conn):
        self.conn = conn

    def get_user_id(self):
        if 'user_id' in session:
            return session['user_id']
        return ''

    def get_user_name(self, user_id):
        try:
            cursor = self.conn.cursor()
            sql = "SELECT name FROM users WHERE id = ?"
            sql_data = (user_id, )
            cursor.execute(sql, sql_data)
            row = cursor.fetchone()
            if row:
                return row['name']
            return '???'
        except sqlite3.Error as err:
            abort(500, description="Error database - get_user_name")

    def logout(self):
        if 'user_id' in session:
            session.pop('user_id')


    def check_login(self, login):
        #login = login.lower()
        if len(login) < 3:
            return 'Login name should be great than 3 characters'
        elif len(login) > 10:
            return 'Login name should be less than 10 characters'
        result = re.match(r'^[a-z0-9_]+$', login)
        if result and result.span():
            result = re.match(r'^[a-z]', login)
            if result and result.span():
                return ''
            return 'Login should start only from letter'
        else:
            return 'Login should contain only letters, numbers or underscores. Letters are insensitive.'

    def check_your_name(self, name):
        #name = re.sub(r' +', ' ', name.strip())
        if len(name) < 3:
            return 'Your name should be great than 3 characters'
        elif len(name) > 20:
            return 'Your name should be less than 20 characters'
        result = re.match(r'^[A-Za-z ]+$', name)
        if result and result.span():
            return ''
        else:
            return 'Your name should contain only letters or spaces.'

    def check_passwords(self, password, password2):
        if len(password) < 6:
            return 'Password length should have min 6 characters'
        if (password != password2):
            return 'Passwords are different. Please try again'
        return ''

    def check_login_isset(self, login):
        try:
            cursor = self.conn.cursor()
            sql = "SELECT id FROM users WHERE login = ?"
            sql_data = (login,)
            cursor.execute(sql, sql_data)
            row = cursor.fetchone()
            if row:
                return f'Login name: "{login}" already exist. Please type other login name'
            return ''
        except sqlite3.Error as err:
            abort(500, description="Error database - check_login_isset")

    def insert_user(self, login, name, password):
        now = datetime.datetime.now()
        format_string = "%Y-%m-%d %H:%M:%S"
        now_string = now.strftime(format_string)
        try:
            cursor = self.conn.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            sql = "INSERT INTO users (login, password, name, updated_at) VALUES (?, ?, ?, ?)"
            sql_data = (login, hashed_password, name, now_string)
            cursor.execute(sql, sql_data)
            self.conn.commit()
        except sqlite3.Error as err:
            abort(500, description="Error database - insert_user")

    def check_credentials(self, login, password):
        try:
            cursor = self.conn.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            sql = "SELECT id FROM users WHERE login = ? and password = ?"
            sql_data = (login.lower(), hashed_password)
            cursor.execute(sql, sql_data)
            row = cursor.fetchone()
            if not row:
                return 'Login and / or password are incorrect. Please try again'
            else:
                session['user_id'] = row['id']
            return ''
        except sqlite3.Error as err:
            abort(500, description="Error database - check_credentials")
