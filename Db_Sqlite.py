import sqlite3

import globals


class DbSqlite:
    def __init__(self):
        self.connection = sqlite3.connect(globals.SQLITE_FILE)
        self.cursor = self.connection.cursor()

    def check_setup(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stockname TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                trade_date TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS trade_history (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stockname TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                sum_buy REAL NOT NULL,
                sum_sell REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS full_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stockname TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                trade_date TEXT NOT NULL,
        ''')
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
        self.connection = None
        self.cursor = None

