import sqlite3, json, re
from flask import abort
class Utils:
    def __init__(self, conn):
        self.conn = conn

    def create_uri_name(self, name):
        name = re.sub(r'[^A-Za-z0-9]', '-', name).lower()
        return re.sub(r'-+', '-', name)

    def update_departments(self, departments):
        try:
            departments = json.loads(departments)
            cursor = self.conn.cursor()
            for department in departments['departments']:
                cursor.execute("SELECT id FROM departments WHERE department_id = ?",
                              (department['departmentId'],))
                result = cursor.fetchone()
                if not result:
                    cursor = self.conn.cursor()
                    cursor.execute("INSERT INTO departments (department_id, name, name_uri) VALUES (?, ?, ?)",
                                  (department['departmentId'], department['displayName'],
                                   self.create_uri_name(department['displayName'])))
                    self.conn.commit()                
        except sqlite3.Error as err:
            abort(500, description="Error database")

    def get_departament_id(self, name_uri):
        try:
            cursor = self.conn.cursor()
            sql = "SELECT department_id FROM departments WHERE name_uri = ?"
            sql_data = (name_uri, )
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result:
                return result['department_id']
            return 1
        except sqlite3.Error as err:
            abort(500, description="Error database")

    def get_items(self, result):
        return json.loads(result.text)['objectIDs']

    def filter_items(self, items, user_id, dep):
        try:
            cursor = self.conn.cursor
            sql = "SELECT objectID FROM arts WHERE ((user_id = ?) && (department = ?))"
            sql_data = (user_id, dep)

        except sqlite3.Error as err:
            abort(500, description="Error database")








