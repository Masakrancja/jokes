import datetime
import sqlite3
from flask import abort

class Fav():
    def __init__(self, conn):
        self.conn = conn

    def add_to_favorites(self, user_id, art_id, hash):
        if not self.get_id_by_hash(hash):
            now = datetime.datetime.now()
            format_string = "%Y-%m-%d %H:%M:%S"
            now_string = now.strftime(format_string)
            try:
                cursor = self.conn.cursor()
                sql = "INSERT INTO user_arts (user_id, art_id, hash, updated_at) VALUES (?, ?, ?, ?)"
                sql_data = (user_id, art_id, hash, now_string)
                cursor.execute(sql, sql_data)
                last_id = cursor.lastrowid
                sql = "INSERT INTO user_arts_content (user_arts_id, info, note, updated_at) VALUES (?, ?, ?, ?)"
                sql_data = (last_id, '', -1, now_string)
                cursor.execute(sql, sql_data)
                self.conn.commit()
            except sqlite3.Error as err:
                abort(500, description=f"Error database - add_to_favorites {err}")


    def remove_from_favorites(self, hash):
        id = self.get_id_by_hash(hash)
        if id:
            try:
                cursor = self.conn.cursor()
                sql = "DELETE FROM user_arts_content WHERE user_arts_id = ?"
                sql_data = (id, )
                cursor.execute(sql, sql_data)
                sql = "DELETE FROM user_arts WHERE hash = ?"
                sql_data = (hash, )
                cursor.execute(sql, sql_data)
                self.conn.commit()
            except sqlite3.Error as err:
                abort(500, description=f"Error database - remove_from_favorites {err}")


    def get_id_by_hash(self, hash):
        try:
            cursor = self.conn.cursor()
            sql = "SELECT id FROM user_arts WHERE hash = ?"
            sql_data = (hash, )
            cursor.execute(sql, sql_data)
            row = cursor.fetchone()
            if row:
                return row['id']
            return False
        except sqlite3.Error as err:
            abort(500, description=f"Error database - isset_in_favorites {err}")



