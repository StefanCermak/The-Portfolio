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

    def add_stock_trade(self, stockname: str, quantity: float, invest: float, trade_date: datetime.date):
        if self.db_sqlite is not None:
            self.db_sqlite.add_stock_trade(stockname, quantity, invest, trade_date)

    def sell_stock(self, stockname: str, earnings: float, sell_date: datetime.date):
        if self.db_sqlite is not None:
            self.db_sqlite.sell_stock(stockname, earnings, sell_date)