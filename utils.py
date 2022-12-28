import datetime
import sqlite3, json, re
from flask import abort
class Utils:
    def __init__(self, conn, museum_api):
        self.conn = conn
        self.museum_api = museum_api

    def check_if_update_departments(self, seconds=1000):
        earlier = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
        cursor = self.conn.cursor()
        sql = "SELECT updated_at FROM departments LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            if datetime.datetime.strptime(result['updated_at'], "%Y-%m-%d %H:%M:%S") > earlier:
                return False
        return True

    def check_if_update_arts(self, department_id, seconds=300):
        earlier = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
        cursor = self.conn.cursor()
        sql = "SELECT updated_at FROM arts WHERE department_id = ? LIMIT 1"
        sql_data = (department_id,)
        cursor.execute(sql, sql_data)
        result = cursor.fetchone()
        if result:
            if datetime.datetime.strptime(result['updated_at'], "%Y-%m-%d %H:%M:%S") > earlier:
                return False
        return True

    def get_departments(self):
        departments = self.museum_api.get_departments()
        if departments.status_code == 200:
            return departments.text
        else:
            abort(departments.status_code)

    def get_objects(self, department_id):
        objects = self.museum_api.get_objects(department_id)
        if objects.status_code == 200:
            return objects.text
        else:
            abort(objects.status_code)


    def create_uri_name(self, name):
        name = re.sub(r'[^A-Za-z0-9]', '-', name).lower()
        return re.sub(r'-+', '-', name)

    def get_department_id(self, name_uri):
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

    def update_departments(self, departments):
        now = datetime.datetime.now()
        format_string = "%Y-%m-%d %H:%M:%S"
        now_string = now.strftime(format_string)
        departments = json.loads(departments)
        try:
            for department in departments['departments']:
                cursor = self.conn.cursor()
                cursor.execute("SELECT id FROM departments WHERE department_id = ?",
                       (department['departmentId'],))
                result = cursor.fetchone()
                if result:
                    cursor.execute("UPDATE departments SET department_id = ?, name = ?, name_uri = ?, updated_at = ? "
                                   " WHERE id=?",
                                   (department['departmentId'], department['displayName'],
                                    self.create_uri_name(department['displayName']), now_string, result['id']))
                else:
                    cursor.execute("INSERT INTO departments (department_id, name, name_uri, updated_at) "
                                   "VALUES (?, ?, ?, ?)",
                                   (department['departmentId'], department['displayName'],
                                    self.create_uri_name(department['displayName']), now_string))
                self.conn.commit()
        except sqlite3.Error as err:
            abort(500, description="Error database")

    def update_arts(self, objects, department_id):
        print('department_id', department_id)
        print('objects', objects)



    def get_items(self, result):
        return json.loads(result.text)['objectIDs']

    '''
     def filter_items(self, items, user_id, dep):
        try:
            cursor = self.conn.cursor
            sql = "SELECT objectID FROM arts WHERE ((user_id = ?) && (department = ?))"
            sql_data = (user_id, dep)
            cursor.execute(sql, sql_data)
            result = cursor.fetchall()
            if result:
                pass


        except sqlite3.Error as err:
            abort(500, description="Error database")
   
    '''








