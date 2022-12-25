import sqlite3
database = 'museum.sqlite'
script_file = 'db.sql'

def execute_script(cursor, script_file):
    with open(script_file, encoding='utf-8') as f:
        query = f.read()
    cursor.executescript(query)

if __name__ == '__main__':
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    execute_script(cursor, script_file)
    conn.commit()
    conn.close()
