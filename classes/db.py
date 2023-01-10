import sqlite3
from flask import g, abort
class DB():
    def __init__(self, db_file):
        self.db_file = db_file

    def tables(self):
        """
        Tabele jakie są uzywane w aplikacji
        :return: list
        """
        return ['arts', 'arts_content', 'departments', 'user_arts', 'user_arts_content', 'users']

    def get_db(self):
        """
        Połączenie z bazą danych sqlite
        :return: resource
        """
        if 'db' not in g:
            g.db = sqlite3.connect(
                self.db_file,
                #detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(self):
        """
        Zamknięcie połączenia z bazą danych
        :return: None
        """
        db = g.pop('db', None)
        if db is not None:
            db.close()
        return None

    def check_if_table_exist(self, conn, table):
        """
        Sprawdzenie czy podana tabela w bazie istnieje
        :param conn:
        :param table:
        :return: boolean
        """
        cursor = conn.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name = ?"
        sql_data = (table,)
        cursor.execute(sql, sql_data)
        return True and cursor.fetchone()

    def check_tables(self):
        """
        Sprawdzenie czy wszystkie tabele w db zostały utworzone

        :return: None, error 500
        """
        for table in self.tables():
            if not self.check_if_table_exist(self.get_db(), table):
                abort(500, description="Error database. Table: " + table + " missing. Run script db_init first")
        return None


