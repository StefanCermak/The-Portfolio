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
                invest REAL NOT NULL,
                trade_date TEXT NOT NULL,
                is_active_series INTEGER NOT NULL );''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stockname TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                sum_buy REAL NOT NULL,
                sum_sell REAL NOT NULL );''')
        self.connection.commit()

    def get_stock_set(self):
        self.cursor.execute('SELECT DISTINCT stockname FROM active_trades;')
        rows = self.cursor.fetchall()
        return {row[0] for row in rows}

    def get_current_stock_set(self):
        # Returns a dictionary with stockname as key and a dictionary with current quantity and current invest as value
        self.cursor.execute('SELECT stockname, quantity, invest, trade_date FROM active_trades WHERE is_active_series = 1')
        rows = self.cursor.fetchall()
        dataset = dict()
        for row in rows:
            if row[0] not in dataset:
                dataset[row[0]] = []
            dataset[row[0]].append({'quantity': row[1], 'invest': row[2], 'date': datetime.date.fromisoformat(row[3])})

        return dataset

    def add_stock_trade(self, stockname: str, quantity: float, invest: float, trade_date: datetime.date):
        self.cursor.execute('''
            INSERT INTO active_trades (stockname, quantity, invest, trade_date, is_active_series)
            VALUES (?, ?, ?, ?, 1);
        ''', (stockname, quantity, invest, trade_date.isoformat()))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
        self.connection = None
        self.cursor = None

