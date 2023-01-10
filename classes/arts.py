import datetime
import sqlite3
import json
from flask import abort
class Arts():
    def __init__(self, conn, museum_api):
        self.conn = conn
        self.museum_api = museum_api


    def check_if_update_arts_is_needed(self, department_id, seconds=3600):
        """
        Check if is needed update id of arts in chosen department id
        :param department_id:
        :param seconds:
        :return: True, if param seconds is greats than different between time from
        last saved content to now, otherwise False
        """
        earlier = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
        try:
            cursor = self.conn.cursor()
            sql = "SELECT updated_at FROM arts WHERE department_id = ? LIMIT 1"
            sql_data = (department_id,)
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result:
                if datetime.datetime.strptime(result['updated_at'], "%Y-%m-%d %H:%M:%S") > earlier:
                    return False
            return True
        except sqlite3.Error as err:
            abort(500, description=f"Error database - check_if_update_arts {err}")


    def get_arts(self, department_id):
        """
        Get arts id from museum api and check result
        :param department_id: integer
        :return: collection
        """
        objects = self.museum_api.get_objects(department_id)
        if objects.status_code == 200:
            return json.loads(objects.text)
        else:
            abort(objects.status_code)


    def update_arts(self, arts_id, department_id):
        """
        Update numbers id of arts to database
        :param arts_id: list
        :param department_id: integer
        :return: None
        """
        now = datetime.datetime.now()
        format_string = "%Y-%m-%d %H:%M:%S"
        now_string = now.strftime(format_string)
        try:
            cursor = self.conn.cursor()
            for art_id in arts_id['objectIDs']:
                sql = "SELECT id from arts WHERE art_id = ? and department_id = ?"
                sql_data = (art_id, department_id)
                cursor.execute(sql, sql_data)
                result = cursor.fetchone()
                if result:
                    sql = "UPDATE arts SET updated_at = ? WHERE id = ?"
                    sql_data = (now_string, result['id'])
                    cursor.execute(sql, sql_data)
                else:
                    sql = "INSERT INTO arts (art_id, department_id, updated_at) VALUES (?, ?, ?)"
                    sql_data = (art_id, department_id, now_string)
                    cursor.execute(sql, sql_data)
            self.conn.commit()
        except sqlite3.Error as err:
            abort(500, description=f"Error database - update_arts {err}")


    def get_arts_for_selected_page(self, page, department_id, max_for_page):
        """
        Get numbers id of arts from database for chosen page and limit arts for page
        :param page: integer
        :param department_id: integer
        :param max_for_page:  integer
        :return: list
        """
        result = []
        try:
            cursor = self.conn.cursor()
            sql = "SELECT art_id FROM arts WHERE department_id = ? ORDER BY art_id ASC LIMIT ?, ?"
            sql_data = (department_id, page * max_for_page, max_for_page)
            cursor.execute(sql, sql_data)
            rows = cursor.fetchall()
            for row in rows:
                result.append(row['art_id'])
            return result
        except sqlite3.Error as err:
            abort(500, description=f"Error database - get_objects_for_selected {err}")
