import datetime, hashlib, sqlite3, json, re
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
            abort(500, description="Error database - get_department_name_from_id")

    def get_hash_art(self, art_id, department_id):
        try:
            cursor = self.conn.cursor()
            sql = "SELECT hash FROM arts WHERE art_id = ? and department_id = ?"
            sql_data = (art_id, department_id)
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result:
                return result['hash']
            return None
        except sqlite3.Error as err:
            abort(500, description="Error database - get_hash_art")

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
                    sql = "INSERT INTO arts (art_id, department_id, hash, updated_at) VALUES (?, ?, ?, ?)"
                    sql_data = (object, department_id, hashlib.sha256(str(object).encode() +
                                str(department_id).encode()).hexdigest(), now_string)
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
        tables_to_update = self.tables_to_update()
        tables_to_insert = ['art_id'] + tables_to_update
        cursor = self.conn.cursor()
        r = self.get_object(object)
        data_to_update = []
        for col in tables_to_update:
            if col == 'department_id':
                data_to_update.append(department_id)
            elif col == 'updated_at':
                data_to_update.append(now_string)
            elif col == 'additionalImages':
                data_to_update.append(';'.join(r[col]))
            else:
                data_to_update.append(r[col])
        data_to_insert = [object] + data_to_update
        try:
            sql = "SELECT id FROM arts_content WHERE art_id = ?"
            sql_data = (object,)
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result:
                sql = "UPDATE arts_content SET " + ', '.join([x + ' = ?' for x in tables_to_update]) + \
                      " WHERE art_id = ?"
                data_to_update = tuple(data_to_update + [object])
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
        tables_to_get = self.tables_to_content()
        try:
            cursor = self.conn.cursor()
            for object in objects:
                sql = "SELECT " + ', '.join(tables_to_get) + " FROM arts_content WHERE art_id = ?"
                sql_data = (object,)
                cursor.execute(sql, sql_data)
                row = cursor.fetchone()
                if row:
                    row = dict(row)
                    row['department'] = self.get_department_name_from_id(row['department_id'])
                    row['hash'] = self.get_hash_art(object, row['department_id'])
                    result.append(row)
            return result
        except sqlite3.Error as err:
            abort(500, description="Error database - get_contents")

    def tables_to_content(self):
        return ['isHighlight', 'accessionYear', 'primaryImageSmall', 'objectName', 'title', 'culture',
                'period', 'dynasty', 'reign', 'portfolio', 'artistRole', 'artistDisplayName',
                'artistDisplayBio', 'artistNationality', 'artistBeginDate', 'artistEndDate',
                'artistGender', 'artistWikidata_URL', 'artistULAN_URL', 'medium', 'dimensions',
                'creditLine', 'city', 'state', 'county', 'country', 'classification',
                'linkResource', 'repository', 'objectURL', 'department_id', 'art_id']

    def tables_which_need_names(self):
        tables = self.tables_to_content()
        del tables[tables.index('isHighlight')]
        del tables[tables.index('title')]
        del tables[tables.index('department_id')]
        del tables[tables.index('primaryImageSmall')]
        del tables[tables.index('art_id')]
        return tables

    def tables_to_update(self):
        return ['isHighlight', 'accessionYear', 'primaryImage', 'primaryImageSmall', 'additionalImages',
                'objectName', 'title', 'culture', 'period', 'dynasty', 'reign', 'portfolio', 'artistRole',
                'artistDisplayName', 'artistDisplayBio', 'artistNationality', 'artistBeginDate',
                'artistEndDate', 'artistGender', 'artistWikidata_URL', 'artistULAN_URL', 'medium',
                'dimensions', 'creditLine', 'city', 'state', 'county', 'country', 'classification',
                'linkResource', 'metadataDate', 'repository', 'objectURL', 'department_id', 'updated_at']

    def get_human_name(self, name):
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return name[0:1].upper() + name[1:] + ':'

    def is_link(self, text):
        result = re.match(r'^https?://', str(text))
        if result and result.span():
            return True
        return False

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

    def get_pagination(self, dep_uri, page, pages, max_pages):
        pagination = {}
        if page > 0:
            pagination['prev'] = {'dep_uri': dep_uri, 'page': page - 1, 'disable': 0}
        else:
            pagination['prev'] = {'dep_uri': dep_uri, 'page': None, 'disable': 1}
        if page < pages:
            pagination['next'] = {'dep_uri': dep_uri, 'page': page + 1, 'disable':0}
        else:
            pagination['next'] = {'dep_uri': dep_uri, 'page': None, 'disable':1}
        if pages < max_pages:
            tab_range = range(1, pages + 1)
        else:
            if (pages - page) > max_pages:
                tab_range = range(page, max_pages + page + 1)
            else:
                tab_range = range(page, pages + 1)
        for item in tab_range:
            pagination[item] = {'dep_uri': dep_uri, 'page':item, 'disable': 0}
        return pagination
