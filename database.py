import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None;
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    try:
        sql = '''CREATE TABLE IF NOT EXISTS tasks (
                    id integer PRIMARY KEY,
                    create_time text NOT NULL,
                    start_time text,
                    exec_time integer
                );'''
        cursor = conn.cursor()
        cursor.execute(sql)
    except Error as e:
        print(e)