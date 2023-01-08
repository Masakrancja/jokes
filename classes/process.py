import sqlite3
import datetime
class Process:
    def __init__(self, conn):
        self.conn = conn


    def get_value(self, hash, col):
        result = ''
        try:
            cursor = self.conn.cursor()
            sql = "SELECT id FROM user_arts WHERE hash = ?"
            sql_data = (hash, )
            cursor.execute(sql, sql_data)
            row = cursor.fetchone()
            if row:
                sql = "SELECT " + col + " FROM user_arts_content WHERE user_arts_id = ?"
                sql_data = (row['id'], )
                cursor.execute(sql, sql_data)
                row = cursor.fetchone()
                if row:
                    result = str(row[col])
        except sqlite3.Error:
            pass
        finally:
            return result


    def set_value(self, value, hash, col):
        result = value
        now = datetime.datetime.now()
        format_string = "%Y-%m-%d %H:%M:%S"
        now_string = now.strftime(format_string)
        if col == 'note':
            try:
                value = int(value)
                if value < 0 or value > 10:
                    value = -1
            except ValueError:
                value = -1
        try:
            cursor = self.conn.cursor()
            sql = "SELECT id FROM user_arts WHERE hash = ?"
            sql_data = (hash, )
            cursor.execute(sql, sql_data)
            row = cursor.fetchone()
            if row:
                sql = "UPDATE user_arts_content SET " + col + " = ?, updated_at = ? WHERE user_arts_id = ?"
                sql_data = (value, now_string, row['id'])
                cursor.execute(sql, sql_data)
                self.conn.commit()
                sql = "SELECT " + col + " FROM user_arts_content WHERE user_arts_id = ?"
                sql_data = (row['id'], )
                cursor.execute(sql, sql_data)
                row = cursor.fetchone()
                if row:
                    result = str(row[col])
        except sqlite3.Error:
            pass
        finally:
            return result
