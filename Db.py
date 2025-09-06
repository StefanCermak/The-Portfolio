import datetime


import globals
import Db_Sqlite


class Db:
    def __init__(self):
        if globals.USER_CONFIG["USE_SQLITE"]:
            self.db_sqlite = Db_Sqlite.DbSqlite()
        else:
            self.db_sqlite = None

    def close(self):
        if self.db_sqlite is not None:
            self.db_sqlite.close()
            self.db_sqlite = None

    def get_stock_set(self):
        if self.db_sqlite is not None:
            return self.db_sqlite.get_stock_set()
        else:
            return set()

    def get_current_stock_set(self):
        if self.db_sqlite is not None:
            return self.db_sqlite.get_current_stock_set()
        else:
            return dict()

    def get_history_stock_set(self):
        if self.db_sqlite is not None:
            return self.db_sqlite.get_history_stock_set()
        else:
            return dict()

    def add_stock_trade(self, ticker_symbol: str, quantity: float, invest: float, trade_date: datetime.date):
        if self.db_sqlite is not None:
            self.db_sqlite.add_stock_trade(ticker_symbol, quantity, invest, trade_date)

    def sell_stock(self, stockname: str, earnings: float, sell_date: datetime.date):
        if self.db_sqlite is not None:
            self.db_sqlite.sell_stock(stockname, earnings, sell_date)

    def add_stockname_ticker(self, stockname: str, ticker_symbol: str, replace_existing: bool = False):
        if self.db_sqlite is not None:
            self.db_sqlite.add_stockname_ticker(stockname, ticker_symbol, replace_existing)

    def find_closed_trades(self):
        if self.db_sqlite is not None:
            self.db_sqlite.find_closed_trades()

    def get_ticker_symbol(self, stockname: str):
        if self.db_sqlite is not None:
            return self.db_sqlite.get_ticker_symbol(stockname)
        else:
            return None

    def get_stockname(self, ticker_symbol: str):
        if self.db_sqlite is not None:
            return self.db_sqlite.get_stockname(ticker_symbol)
        else:
            return None

    def get_stocknames_with_tickers(self):
        if self.db_sqlite is not None:
            return self.db_sqlite.get_stocknames_with_tickers()
        else:
            return dict()