import hashlib
import re
import datetime
import sqlite3
from flask import abort, session, flash

class Auth():
    def __init__(self, conn):
        self.conn = conn


    def get_user_id(self):
        """
        Get id logged user from session
        :return: string
        """
        if 'user_id' in session:
            user_id = session['user_id']
            if self.check_if_user_id_exist(user_id):
                return user_id
            else:
                self.logout()
        return ''

    def add_user_to_session(self, user_id):
        """
        Add user id to session
        :param user_id: string
        :return: None
        """
        session['user_id'] = user_id
        return None


    def check_if_user_id_exist(self, user_id):
        """
        Check if id of user isset in database 'users'
        :param user_id: string
        :return: boolean
        """
        try:
            cursor = self.conn.cursor()
            sql = "SELECT id FROM users WHERE user_id = ?"
            sql_data = (user_id, )
            cursor.execute(sql, sql_data)
            row = cursor.fetchone()
            if row:
                return True
            return False
        except sqlite3.Error as err:
            abort(500, description=f"Error database - check_if_user_id_exist {err}")


    def get_user_name(self, user_id):
        """
        Get full name of user by his id
        :param user_id: string
        :return: string
        """
        try:
            cursor = self.conn.cursor()
            sql = "SELECT name FROM users WHERE user_id = ?"
            sql_data = (user_id, )
            cursor.execute(sql, sql_data)
            row = cursor.fetchone()
            if row:
                return row['name']
            return ''
        except sqlite3.Error as err:
            abort(500, description=f"Error database - get_user_name {err}")


    def logout(self):
        """
        Delete id of user from session
        :return: None
        """
        if 'user_id' in session:
            flash(f"See you again {self.get_user_name(session['user_id'])}")
            session.pop('user_id')
        return None


    def check_login(self, login):
        """
        Validate login name
        :param login: string
        :return: string
        """
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
        """
        Validate full name of user
        :param name: string
        :return: string
        """
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
        """
        Validate password
        :param password: string
        :param password2: string
        :return: String
        """
        if len(password) < 6:
            return 'Password length should have min 6 characters'
        if (password != password2):
            return 'Passwords are different. Please try again'
        return ''


    def check_login_isset(self, login):
        """
        check if got login name is set in database
        :param login: string
        :return: boolean
        """
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
            abort(500, description=f"Error database - check_login_isset {err}")


    def insert_user(self, login, name, password):
        """
        Adding user into database
        :param login: string
        :param name: string
        :param password: string
        :return: None
        """
        now = datetime.datetime.now()
        format_string = "%Y-%m-%d %H:%M:%S"
        now_string = now.strftime(format_string)
        try:
            cursor = self.conn.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            hashed_user_id = hashlib.sha256(login.encode() + name.encode()).hexdigest()
            sql = "INSERT INTO users (user_id, login, password, name, updated_at) VALUES (?, ?, ?, ?, ?)"
            sql_data = (hashed_user_id, login, hashed_password, name, now_string)
            cursor.execute(sql, sql_data)
            self.conn.commit()
            self.add_user_to_session(hashed_user_id)
            flash(f"Hello {name}. You account was succefully created")
            flash(f"Hello {self.get_user_name(hashed_user_id)}. You are succefully logged")
        except sqlite3.Error as err:
            abort(500, description=f"Error database - insert_user {err}")


    def check_credentials(self, login, password):
        """
        Check if user sent correct datas during login
        If yes that put his id to session
        :param login: string
        :param password: string
        :return: string
        """
        try:
            cursor = self.conn.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            sql = "SELECT user_id FROM users WHERE login = ? and password = ?"
            sql_data = (login.lower(), hashed_password)
            cursor.execute(sql, sql_data)
            row = cursor.fetchone()
            if not row:
                return 'Login and / or password are incorrect. Please try again'
            else:
                self.add_user_to_session(row['user_id'])
                flash(f"Hello {self.get_user_name(row['user_id'])}. You are succefully logged")
            return ''
        except sqlite3.Error as err:
            abort(500, description=f"Error database - check_credentials {err}")
