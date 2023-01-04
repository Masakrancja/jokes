import datetime, hashlib, sqlite3, json, re
from flask import abort
class Cont():
    def __init__(self, conn, museum_api):
        self.conn = conn
        self.museum_api = museum_api


    def get_content(self, art_id):
        object = self.museum_api.get_object(art_id)
        if object.status_code == 200:
            return json.loads(object.text)
        else:
            abort(object.status_code)


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
        r = self.get_content(object)
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


    def get_cols_names_from_table(self, table):
        result = []
        try:
            cursor = self.conn.cursor();
            sql = "SELECT names FROM pragma_table_info(?)"
            sql_data = (table,)
            cursor.execute(sql, sql_data)
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    result.append(row['name'])
            return result
        except sqlite3.Error as err:
            abort(500, description=f"Error database - update_content {err}")