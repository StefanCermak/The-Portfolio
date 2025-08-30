import sqlite3
import datetime

import globals


class DbSqlite:
    def __init__(self):
        self.connection = sqlite3.connect(globals.SQLITE_FILE)
        self.cursor = self.connection.cursor()
        self.check_setup()

    def check_setup(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stockname TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                trade_date TEXT NOT NULL );''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stockname TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                sum_buy REAL NOT NULL,
                sum_sell REAL NOT NULL );''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS full_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stockname TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                trade_date TEXT NOT NULL );''')
        self.connection.commit()

    def get_stock_set(self):
        self.cursor.execute('SELECT DISTINCT stockname FROM active_trades;')
        rows = self.cursor.fetchall()
        return {row[0] for row in rows}

    def add_stock_trade(self, stockname: str, quantity: float, price: float, trade_date: datetime.date):
        self.cursor.execute('''
            INSERT INTO active_trades (stockname, quantity, price, trade_date)
            VALUES (?, ?, ?, ?);
        ''', (stockname, quantity, price, trade_date.isoformat()))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
        self.connection = None
        self.cursor = None

