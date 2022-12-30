import datetime
import sqlite3, json, re
from flask import abort
class Utils:
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

    def check_if_update_arts(self, department_id, seconds=1800):
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
            abort(500, description="Error database - check_if_update_arts")

    def get_departments(self):
        departments = self.museum_api.get_departments()
        if departments.status_code == 200:
            return json.loads(departments.text)
        else:
            abort(departments.status_code)

    def get_objects(self, department_id):
        objects = self.museum_api.get_objects(department_id)
        if objects.status_code == 200:
            return json.loads(objects.text)
        else:
            abort(objects.status_code)

    def get_object(self, art_id):
        object = self.museum_api.get_object(art_id)
        if object.status_code == 200:
            return json.loads(object.text)
        else:
            abort(object.status_code)


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
            abort(500, description="Error database - get_department_id")

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

    def update_arts(self, objects, department_id):
        now = datetime.datetime.now()
        format_string = "%Y-%m-%d %H:%M:%S"
        now_string = now.strftime(format_string)
        try:
            cursor = self.conn.cursor()
            for object in objects['objectIDs']:
                sql = "SELECT id from arts WHERE art_id = ? and department_id = ?"
                sql_data = (object, department_id)
                cursor.execute(sql, sql_data)
                result = cursor.fetchone()
                if result:
                    sql = "UPDATE arts SET updated_at = ? WHERE id = ?"
                    sql_data = (now_string, result['id'])
                    cursor.execute(sql, sql_data)
                else:
                    sql = "INSERT INTO arts (art_id, department_id, updated_at) VALUES (?, ?, ?)"
                    sql_data = (object, department_id, now_string)
                    cursor.execute(sql, sql_data)
            self.conn.commit()
        except sqlite3.Error as err:
            abort(500, description="Error database - update_arts")

    def get_pages_count(self, department_id, max_for_page):
        try:
            cursor = self.conn.cursor()
            sql = "SELECT COUNT(id) AS c FROM arts WHERE department_id = ?"
            sql_data = (department_id,)
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if max_for_page == 0:
               max_for_page = 10
            pages =  result['c'] // max_for_page
            if (result['c'] % max_for_page) > 0:
                pages += 1
            return pages
        except sqlite3.Error as err:
            abort(500, description="Error database - get_pages_count")


    def get_objects_for_selected(self, page, department_id, max_for_page):
        try:
            result = []
            cursor = self.conn.cursor()
            sql = "SELECT art_id FROM arts WHERE department_id = ? ORDER BY art_id ASC LIMIT ?, ?"
            sql_data = (department_id, page * max_for_page, max_for_page)
            cursor.execute(sql, sql_data)
            rows = cursor.fetchall()
            for row in rows:
                result.append(row['art_id'])
            return result
        except sqlite3.Error as err:
            abort(500, description="Error database - get_objects_for_selected")

    def check_if_update_art_content(self, object, department_id, seconds=1800):
        earlier = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
        try:
            cursor = self.conn.cursor()
            sql = "SELECT updated_at FROM arts_content WHERE art_id = ? and department_id = ?"
            sql_data = (object, department_id)
            cursor.execute(sql, sql_data);
            result = cursor.fetchone()
            if result:
                if datetime.datetime.strptime(result['updated_at'], "%Y-%m-%d %H:%M:%S") > earlier:
                    return False
            return True
        except sqlite3.Error as err:
            abort(500, description="Error database - check_if_update_art_content")

    def update_content(self, object, department_id):
        now = datetime.datetime.now()
        format_string = "%Y-%m-%d %H:%M:%S"
        now_string = now.strftime(format_string)
        tables_to_update = ['isHighlight', 'accessionYear', 'primaryImage', 'primaryImageSmall', 'additionalImages',
                            'objectName', 'title', 'culture', 'period', 'dynasty', 'reign', 'portfolio', 'artistRole',
                            'artistDisplayName', 'artistDisplayBio', 'artistNationality', 'artistBeginDate',
                            'artistEndDate', 'artistGender', 'artistWikidata_URL', 'artistULAN_URL', 'medium',
                            'dimensions', 'creditLine', 'city', 'state', 'county', 'country', 'classification',
                            'linkResource', 'metadataDate', 'repository', 'objectURL', 'department_id', 'updated_at']
        tables_to_insert = ['art_id'] + tables_to_update
        cursor = self.conn.cursor()
        r = self.get_object(object)

        print(r)


        data_to_update = [r['isHighlight'], r['accessionYear'], r['primaryImage'], r['primaryImageSmall'],
                          ';'.join(r['additionalImages']), r['objectName'], r['title'], r['culture'], r['period'], r['dynasty'],
                          r['reign'], r['portfolio'], r['artistRole'], r['artistDisplayName'], r['artistDisplayBio'],
                          r['artistNationality'], r['artistBeginDate'], r['artistEndDate'], r['artistGender'],
                          r['artistWikidata_URL'], r['artistULAN_URL'], r['medium'], r['dimensions'], r['creditLine'],
                          r['city'], r['state'], r['county'], r['country'], r['classification'], r['linkResource'],
                          r['metadataDate'], r['repository'], r['objectURL'], department_id, now_string]

        data_to_insert = [object] + data_to_update
        try:
            sql = "SELECT id FROM arts_content WHERE art_id = ?"
            sql_data = (object,)
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result:
                sql = "UPDATE arts_content SET " + ', '.join([x + ' = ?' for x in tables_to_update]) + \
                      " WHERE art_id = ?"
                print(sql)
                data_to_update = tuple(data_to_update + [object])
                print(data_to_update)
                cursor.execute(sql, data_to_update)
            else:
                sql = "INSERT INTO arts_content (" + ', '.join(tables_to_insert) + ") VALUES (" + ', '.join(
                    len(tables_to_insert) * '?') + ")"
                data_to_insert = tuple(data_to_insert)
                cursor.execute(sql, data_to_insert)
            self.conn.commit()
        except sqlite3.Error as err:
            abort(500, description="Error database - update_content")

    def get_contents(self, objects):
        result = []
        try:
            cursor = self.conn.cursor()
            for object in objects:
                sql = "SELECT * FROM arts_content WHERE art_id = ?"
                sql_data = (object,)
                cursor.execute(sql, sql_data)
                row = cursor.fetchone()
                if row:
                    result.append(dict(row))
            return result
        except sqlite3.Error as err:
            abort(500, description="Error database - get_contents")




