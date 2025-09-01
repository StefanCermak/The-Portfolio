import sqlite3
import datetime

import globals


class DbSqlite:
    def __init__(self):
        self.connection = sqlite3.connect(globals.SQLITE_FILE)
        self.cursor = self.connection.cursor()
        self.check_setup()

    def check_setup(self):
        self.cursor.execute('''PRAGMA foreign_keys = ON;''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_name_ticker_names (
                ticker_symbol TEXT PRIMARY KEY,
                stockname TEXT NOT NULL);''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker_symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                invest REAL NOT NULL,
                trade_date TEXT NOT NULL,
                is_active_series INTEGER NOT NULL CHECK (is_active_series IN (0, 1)),
                FOREIGN KEY (ticker_symbol) REFERENCES stock_name_ticker_names(ticker_symbol));''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker_symbol TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                sum_buy REAL NOT NULL,
                sum_sell REAL NOT NULL,
                FOREIGN KEY (ticker_symbol) REFERENCES stock_name_ticker_names(ticker_symbol));''')
        self.connection.commit()

    def get_stock_set(self):
        self.cursor.execute('''SELECT DISTINCT s.stockname
                               FROM active_trades a
                               JOIN stock_name_ticker_names s ON a.ticker_symbol = s.ticker_symbol
                               WHERE a.is_active_series = 1;''')
        rows = self.cursor.fetchall()
        return {row[0] for row in rows}

    def get_current_stock_set(self):
        # Returns a dictionary with stockname as key and a dictionary with current quantity and current invest as value
        self.cursor.execute('''SELECT s.stockname, a.quantity, a.invest, a.trade_date
                               FROM active_trades a
                               JOIN stock_name_ticker_names s ON a.ticker_symbol = s.ticker_symbol
                               WHERE a.is_active_series = 1;''')
        rows = self.cursor.fetchall()
        dataset = dict()
        for row in rows:
            if row[0] not in dataset:
                dataset[row[0]] = []
            dataset[row[0]].append({'quantity': row[1], 'invest': row[2], 'date': datetime.date.fromisoformat(row[3])})

        return dataset

    def get_history_stock_set(self):
        self.cursor.execute('''SELECT s.stockname, h.start_date, h.end_date, h.sum_buy, h.sum_sell
                               FROM trade_history h
                               JOIN stock_name_ticker_names s ON h.ticker_symbol = s.ticker_symbol;''')
        rows = self.cursor.fetchall()
        dataset = dict()
        for row in rows:
            if row[0] not in dataset:
                dataset[row[0]] = []
            dataset[row[0]].append({'start_date': datetime.date.fromisoformat(row[1]),
                                   'end_date': datetime.date.fromisoformat(row[2]),
                                   'sum_buy': row[3],
                                   'sum_sell': row[4]})
        return dataset

    def add_stock_trade(self, ticker_symbol: str, quantity: float, invest: float, trade_date: datetime.date):
        self.cursor.execute('''
            INSERT INTO active_trades (ticker_symbol, quantity, invest, trade_date, is_active_series)
            VALUES (?, ?, ?, ?, 1);
        ''', (ticker_symbol, quantity, invest, trade_date.isoformat()))
        self.connection.commit()

    def sell_stock(self, stockname: str, earnings: float, sell_date: datetime.date):
        # collect sum of invests, quantity for all active trades for this stock
        self.cursor.execute('''
            SELECT MIN(a.trade_date) as start_date,
                   SUM(a.quantity) as total_quantity,
                   SUM(a.invest) as total_invest
            FROM active_trades a
            JOIN stock_name_ticker_names s ON a.ticker_symbol = s.ticker_symbol
            WHERE s.stockname = ? AND a.is_active_series = 1;
        ''', (stockname,))
        row = self.cursor.fetchone()
        if not row or row[0] is None or row[1] is None or row[2] is None:
            return  # no active trades for this stock
        start_date, total_quantity, total_invest = row
        ticker_symbol = self.get_ticker_symbol(stockname)
        self.cursor.execute('''
            INSERT INTO trade_history (ticker_symbol, start_date, end_date, sum_buy, sum_sell)
            VALUES (?, ?, ?, ?, ?);
        ''', (ticker_symbol, start_date, sell_date.isoformat(), total_invest, earnings))
        # mark all active trades for this stock as inactive
        self.cursor.execute('''
            UPDATE active_trades
            SET is_active_series = 0
            WHERE ticker_symbol = ? AND is_active_series = 1;
            ''', (ticker_symbol,))
        self.connection.commit()

    def add_stockname_ticker(self, stockname: str, ticker_symbol: str):
        self.cursor.execute('''
            INSERT OR REPLACE INTO stock_name_ticker_names (ticker_symbol, stockname)
            VALUES (?, ?);
        ''', (ticker_symbol, stockname))
        self.connection.commit()

    def get_ticker_symbol(self, stockname: str):
        self.cursor.execute('SELECT ticker_symbol FROM stock_name_ticker_names WHERE stockname = ?;', (stockname,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def close(self):
        self.cursor.close()
        self.connection.close()
        self.connection = None
        self.cursor = None
