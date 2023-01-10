import datetime, sqlite3, json, re
from flask import abort
class Departments():
    def __init__(self, conn, museum_api):
        self.conn = conn
        self.museum_api = museum_api

    def check_if_update_departments(self, seconds=3600):
        earlier = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
        cursor = self.conn.cursor()
        try:
            sql = "SELECT updated_at FROM departments LIMIT 1"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                if datetime.datetime.strptime(result['updated_at'], "%Y-%m-%d %H:%M:%S") > earlier:
                    return False
            return True
        except sqlite3.Error as err:
            abort(500, description="Error database - check_if_update_departments")

    def get_departments(self):
        departments = self.museum_api.get_departments()
        if departments.status_code == 200:
            return json.loads(departments.text)
        else:
            abort(departments.status_code)

    def update_departments(self, departments):
        now = datetime.datetime.now()
        format_string = "%Y-%m-%d %H:%M:%S"
        now_string = now.strftime(format_string)
        try:
            cursor = self.conn.cursor()
            for department in departments['departments']:
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
            abort(500, description="Error database - update_departments")

    def get_departments_from_db(self):
        result = []
        try:
            cursor = self.conn.cursor()
            sql = "SELECT department_id, name, name_uri FROM departments ORDER BY name ASC"
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(row))
            return result
        except sqlite3.Error as err:
            abort(500, description="Error database - get_departments_from_db")

    def get_department_id_from_uri(self, name_uri):
        try:
            cursor = self.conn.cursor()
            sql = "SELECT department_id FROM departments WHERE name_uri = ?"
            sql_data = (name_uri, )
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result:
                return result['department_id']
            return None
        except sqlite3.Error as err:
            abort(500, description="Error database - get_department_id_from_uri")


    def get_department_name_from_id(self, department_id):
        try:
            cursor = self.conn.cursor()
            sql = "SELECT name FROM departments WHERE department_id = ?"
            sql_data = (department_id, )
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result:
                return result['name']
            return 1
        except sqlite3.Error as err:
            abort(500, description=f"Error database - get_department_name_from_id {err}")

    def create_uri_name(self, name):
        name = re.sub(r'[^A-Za-z0-9]', '-', name).lower()
        return re.sub(r'-+', '-', name)
