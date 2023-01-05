import datetime
import sqlite3
import json
import re
from flask import abort
class Cont():
    def __init__(self, conn, museum_api):
        self.conn = conn
        self.museum_api = museum_api
        self.cols_to_update = self.get_cols_to_update(table="arts_content")
        self.cols_to_insert = self.get_cols_to_insert(table="arts_content")
        self.cols_to_content = self.get_cols_to_content(table="arts_content")


    def get_content(self, art_id):
        object = self.museum_api.get_object(art_id)
        if object.status_code == 200:
            return json.loads(object.text)
        else:
            abort(object.status_code, description="Error museum api")


    def check_if_update_art_content_is_needed(self, art_id, department_id, seconds=3600):
        earlier = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
        try:
            cursor = self.conn.cursor()
            sql = "SELECT updated_at FROM arts_content WHERE art_id = ? and department_id = ?"
            sql_data = (art_id, department_id)
            cursor.execute(sql, sql_data);
            result = cursor.fetchone()
            if result:
                if datetime.datetime.strptime(result['updated_at'], "%Y-%m-%d %H:%M:%S") > earlier:
                    return False
            return True
        except sqlite3.Error as err:
            abort(500, description=f"Error database - check_if_update_art_content {err}")


    def update_content(self, art_id, department_id):
        now = datetime.datetime.now()
        format_string = "%Y-%m-%d %H:%M:%S"
        now_string = now.strftime(format_string)
        cursor = self.conn.cursor()
        r = self.get_content(art_id)
        data_to_update = []
        for col in self.cols_to_update:
            if col == 'department_id':
                data_to_update.append(department_id)
            elif col == 'updated_at':
                data_to_update.append(now_string)
            elif col == 'additionalImages':
                data_to_update.append(';'.join(r[col]))
            else:
                data_to_update.append(r[col])
        data_to_insert = [art_id] + data_to_update
        try:
            sql = "SELECT id FROM arts_content WHERE art_id = ?"
            sql_data = (art_id,)
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result:
                sql = "UPDATE arts_content SET " + ', '.join([x + ' = ?' for x in self.cols_to_update]) + \
                      " WHERE art_id = ?"
                data_to_update = tuple(data_to_update + [art_id])
                cursor.execute(sql, data_to_update)
            else:
                sql = "INSERT INTO arts_content (" + ', '.join(self.cols_to_insert) + ") VALUES (" + ', '.join(
                    len(self.cols_to_insert) * '?') + ")"
                data_to_insert = tuple(data_to_insert)
                cursor.execute(sql, data_to_insert)
            self.conn.commit()
        except sqlite3.Error as err:
            abort(500, description=f"Error database - update_content {err}")


    def get_cols_names_from_table(self, table:str) -> list:
        result = []
        try:
            cursor = self.conn.cursor();
            sql = "SELECT name FROM pragma_table_info(?)"
            sql_data = (table,)
            cursor.execute(sql, sql_data)
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    result.append(row['name'])
            return result
        except sqlite3.Error as err:
            abort(500, description=f"Error database - update_content {err}")


    def del_cols_names_from_table(self, cols:list, cols_to_delete:list) -> list:
        for col_to_delete in cols_to_delete:
            if col_to_delete in cols:
                del cols[cols.index(col_to_delete)]
        return cols


    def get_cols_to_update(self, table="arts_content"):
        cols_to_delete = ['id', 'art_id']
        cols = self.get_cols_names_from_table(table)
        return self.del_cols_names_from_table(cols, cols_to_delete)


    def get_cols_to_insert(self, table="arts_content"):
        cols_to_delete = ['id']
        cols = self.get_cols_names_from_table(table)
        return self.del_cols_names_from_table(cols, cols_to_delete)

    def get_cols_to_content(self, table="arts_content"):
        cols_to_delete = ['id', 'primaryImage', 'additionalImages', 'metadataDate', 'updated_at']
        cols = self.get_cols_names_from_table(table)
        return self.del_cols_names_from_table(cols, cols_to_delete)


    def get_contents(self, arts_id):
        result = []
        try:
            cursor = self.conn.cursor()
            for art_id in arts_id:
                sql = "SELECT " + ', '.join(self.cols_to_content) + " FROM arts_content WHERE art_id = ?"
                sql_data = (art_id,)
                cursor.execute(sql, sql_data)
                row = cursor.fetchone()
                if row:
                    tab = {}
                    row = dict(row)
                    tab['hash'] = self.get_hash_art(art_id, row['department_id'])
                    tab['title'] = row.pop('title')
                    tab['image'] = row.pop('primaryImageSmall')
                    row.pop('art_id')
                    tab['info'] = row
                    result.append({art_id:tab})
            return result
        except sqlite3.Error as err:
            abort(500, description=f"Error database - get_contents {err}")


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
            abort(500, description=f"Error database - get_hash_art {err}")


    def get_human_name(self, name):
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return name[0:1].upper() + name[1:] + ':'


    def get_cols_to_need_names(self, table="arts_content"):
        cols_to_delete = ['id', 'art_id', 'primaryImage', 'primaryImageSmall', 'additionalImages', 'title',
                          'metadataDate', 'department_id', 'updated_at']
        cols = self.get_cols_names_from_table(table)
        return self.del_cols_names_from_table(cols, cols_to_delete)

    def get_contents_from_user(self, contents, user_id):
        if user_id:
           for content in contents:
               pass



