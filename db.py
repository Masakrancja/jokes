import sqlite3
from flask import g, abort
class DB():
    def __init__(self, db_file):
        self.db_file = db_file

    def tables(self):
        return ['art_department', 'arts', 'users', 'departments']

    def get_db(self):
        if 'db' not in g:
            g.db = sqlite3.connect(
                self.db_file,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(self):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def check_if_table_exist(self, conn, table):
        cursor = conn.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name = ?"
        sql_data = (table,)
        cursor.execute(sql, sql_data)
        return True and cursor.fetchone()

    def check_tables(self):
        for table in self.tables():

            print('table', table)

            if not self.check_if_table_exist(self.get_db(), table):
                abort(500, description="Error database. Table: " + table + " missing. Run script db_init first")


