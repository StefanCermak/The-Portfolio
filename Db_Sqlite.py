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

    def sell_stock(self, stockname: str, earnings: float, sell_date: datetime.date):
        # collect sum of invests, quantity for all active trades for this stock
        self.cursor.execute('''
            SELECT MIN(trade_date) as start_date, SUM(quantity) as total_quantity, SUM(invest) as total_invest
            FROM active_trades
            WHERE stockname = ? AND is_active_series = 1;
        ''', (stockname,))
        row = self.cursor.fetchone()
        if not row or row[0] is None or row[1] is None or row[2] is None:
            return  # no active trades for this stock
        start_date, total_quantity, total_invest = row

        self.cursor.execute('''
            INSERT INTO trade_history (stockname, start_date, end_date, sum_buy, sum_sell)
            VALUES (?, ?, ?, ?, ?);
            ''', (stockname, start_date, sell_date.isoformat(), total_invest, earnings))
        # mark all active trades for this stock as inactive
        self.cursor.execute('''
            UPDATE active_trades
            SET is_active_series = 0
            WHERE stockname = ? AND is_active_series = 1;
            ''', (stockname,))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
        self.connection = None
        self.cursor = None
