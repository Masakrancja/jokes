import sqlite3
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
                sql = "SELECT ? FROM user_arts_content WHERE user_arts_id = ?"
                sql_data = (col, row['id'])
                cursor.execute(sql, sql_data)
                row = cursor.fetchone()
                if row:
                    result = row[col]
        except sqlite3.Error:
            pass
        finally:
            return result

    def set_value(self, text, hash, col):
        result = ''