import datetime, sqlite3, json, re
from flask import abort


class Departments():
    def __init__(self, conn, museum_api):
        self.conn = conn
        self.museum_api = museum_api


    def check_if_update_departments(self, seconds=86400):
        """
        Check if is needed update content of depatmrnts
        :param seconds: Integer
        :return: Boolean
        """
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
        """
        Get struct of depatmrnts from museum api and check result
        :return: collection
        """
        departments = self.museum_api.get_departments()
        if departments.status_code == 200:
            return json.loads(departments.text)
        else:
            abort(departments.status_code)


    def update_departments(self, departments):
        """
        Update info about departments to database
        :param departments:list of dicts
        :return: None
        """
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
        """
        Get departments from database
        :return: list of dicts
        """
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
        """
        Get department id by uri name
        :param name_uri: string
        :return: Integer
        """
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
        """
        Get departmrnt name by department id
        :param department_id: Integer
        :return: String
        """
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
        """
        Create friendly name to browser
        :param name: string
        :return: string
        """
        name = re.sub(r'[^A-Za-z0-9]', '-', name).lower()
        return re.sub(r'-+', '-', name)


    def get_correct_me(self, user_id, me):
        """
        Get and correct param 'me' if needed
        :param user_id: string
        :param me: string
        :return: string
        """
        avail = ['all', 'only-me']
        if me not in avail:
            return 'all'
        if not user_id and me == 'only-me':
            return 'all'
        return me


    def get_all_counts_in_departments(self, departments):
        """
        Get counted all arts by particulary department
        :param departments: List of dicts
        :return: list
        """
        for i, department in enumerate(departments):
            try:
                cursor = self.conn.cursor()
                sql = "SELECT COUNT(id) AS c FROM arts WHERE department_id = ?"
                sql_data = (department['department_id'], )
                cursor.execute(sql, sql_data)
                row = cursor.fetchone()
                departments[i]['count'] = row['c']
            except sqlite3.Error:
                departments[i]['count'] = 0
        return departments


    def get_all_user_counts_in_departments(self, departments, user_id):
        """
        Get countig all arts but only added to favorites by lggged user in all departments
        :param departments: list of dicts
        :param user_id: string
        :return: list
        """
        for i, department in enumerate(departments):
            try:
                cursor = self.conn.cursor()
                sql = "SELECT COUNT(a.id) AS c FROM arts AS a " \
                      "INNER JOIN user_arts AS ua ON a.art_id = ua.art_id " \
                      "WHERE ua.user_id = ? and a.department_id = ?"
                sql_data = (user_id, department['department_id'])
                cursor.execute(sql, sql_data)
                row = cursor.fetchone()
                departments[i]['count'] = row['c']
            except sqlite3.Error:
                departments[i]['count'] = 0
        return departments
