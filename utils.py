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
            print(err)
            abort(500, description="Error database")
