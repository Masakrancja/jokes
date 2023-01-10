import hashlib
import re
import datetime
import sqlite3
from flask import abort, session

class Auth():
    def __init__(self, conn):
        self.conn = conn


    def get_user_id(self):
        """
        Pobranie id zalogowanego usera z sesji
        :return: string
        """
        if 'user_id' in session:
            user_id = session['user_id']
            if self.check_if_user_id_exist(user_id):
                return user_id
            else:
                self.logout()
        return ''

    def check_if_user_id_exist(self, user_id):
        """
        Sprawdzenie czy id usera już istnieje w bazie 'users'
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
        Pobrane pełnej nazwy usera na postawie jego identyfikatora
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
        Usunięcie id usera z sesji
        :return: None
        """
        if 'user_id' in session:
            session.pop('user_id')
        return None


    def check_login(self, login):
        """
        Walidacja loginu
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
        Walidacja pełnej nazwy usera
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
        Walidacja hasła
        :param password: string
        :param password2: string
        :return:
        """
        if len(password) < 6:
            return 'Password length should have min 6 characters'
        if (password != password2):
            return 'Passwords are different. Please try again'
        return ''


    def check_login_isset(self, login):
        """
        Sprawdzenie czy podany login już istnieje w db
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
        Dodanie usera do db
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
        except sqlite3.Error as err:
            abort(500, description=f"Error database - insert_user {err}")


    def check_credentials(self, login, password):
        """
        Sprawdzenie czy user podał poprawne dane podczas logowania
        a jeżeli tak to wstawienie jego identyfikatora do sesji
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
                session['user_id'] = row['user_id']
            return ''
        except sqlite3.Error as err:
            abort(500, description=f"Error database - check_credentials {err}")
