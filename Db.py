import datetime
from typing import Any, Dict, List, Set, Optional

import globals
import Db_Sqlite
"""
This file is part of "The Portfolio".

"The Portfolio"is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

"The Portfolio" is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>. 
"""

""" Database wrapper class to handle different database backends. Currently supports SQLite. """

class Db:
    _instance = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "Db":
        """
        Create or return the singleton instance of the Db class.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the database backend based on user configuration.
        """
        if globals.USER_CONFIG["USE_SQLITE"]:
            self.db_sqlite = Db_Sqlite.DbSqlite()
        else:
            self.db_sqlite = None

    def close(self) -> None:
        """
        Close the database connection if it is open.
        """
        if self.db_sqlite is not None:
            self.db_sqlite.close()
            self.db_sqlite = None

    def get_stock_set(self) -> Set[str]:
        """
        Get a set of all stock names with active trades.

        Returns:
            set: Set of stock names.
        """
        if self.db_sqlite is not None:
            return self.db_sqlite.get_stock_set()
        else:
            return set()

    def get_current_stock_set(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a dictionary of current active trades grouped by stock name.

        Returns:
            dict: Dictionary with stock name as key and a list of trade info dicts as value.
        """
        if self.db_sqlite is not None:
            return self.db_sqlite.get_current_stock_set()
        else:
            return dict()

    def get_history_stock_set(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a dictionary of historical trades grouped by stock name.

        Returns:
            dict: Dictionary with stock name as key and a list of trade history dicts as value.
        """
        if self.db_sqlite is not None:
            return self.db_sqlite.get_history_stock_set()
        else:
            return dict()

    def get_quantity_of_stock(self, stockname: str) -> Optional[float]:
        """
        Get the total quantity of a given stock currently held.

        Args:
            stockname (str): The name of the stock.

        Returns:
            float or None: Total quantity or None if not found.
        """
        if self.db_sqlite is not None:
            return self.db_sqlite.get_quantity_of_stock(stockname)
        else:
            return None

    def add_stock_trade(self, ticker_symbol: str, quantity: float, invest: float, trade_date: datetime.date) -> None:
        """
        Add a new stock trade to the active trades table.

        Args:
            ticker_symbol (str): The ticker symbol.
            quantity (float): The quantity traded.
            invest (float): The invested amount.
            trade_date (datetime.date): The date of the trade.
        """
        if self.db_sqlite is not None:
            self.db_sqlite.add_stock_trade(ticker_symbol, quantity, invest, trade_date)

    def sell_stock(self, stockname: str, earnings: float, sell_date: datetime.date) -> None:
        """
        Sell all active trades for a given stock, move them to history, and mark as inactive.

        Args:
            stockname (str): The name of the stock.
            earnings (float): The total earnings from the sale.
            sell_date (datetime.date): The date of the sale.
        """
        if self.db_sqlite is not None:
            self.db_sqlite.sell_stock(stockname, earnings, sell_date)

    def add_dividend_payment(self, ticker_symbol: str, payment_date: datetime.date, amount: float) -> None:
        """
        Add a dividend payment record.

        Args:
            ticker_symbol (str): The ticker symbol.
            payment_date (datetime.date): The date of the payment.
            amount (float): The amount paid.
        """
        if self.db_sqlite is not None:
            self.db_sqlite.add_dividend_payment(ticker_symbol, payment_date, amount)

    def get_dividend_payments(self) -> List[Dict[str, Any]]:
        """
        Get all dividend payment records.

        Returns:
            list: List of dividend payment records as dicts.
        """
        if self.db_sqlite is not None:
            return self.db_sqlite.get_dividend_payments()
        else:
            return []

    def add_stockname_ticker(self, stockname: str, ticker_symbol: str, replace_existing: bool = False) -> None:
        """
        Add or update a stock name and ticker symbol mapping.

        Args:
            stockname (str): The name of the stock.
            ticker_symbol (str): The ticker symbol.
            replace_existing (bool): If True, replace existing mapping.
        """
        if self.db_sqlite is not None:
            self.db_sqlite.add_stockname_ticker(stockname, ticker_symbol, replace_existing)

    def find_closed_trades(self) -> None:
        """
        Find and close trade series where all shares have been sold, moving them to trade history.
        """
        if self.db_sqlite is not None:
            self.db_sqlite.find_closed_trades()

    def get_ticker_symbol(self, stockname: str) -> Optional[str]:
        """
        Get the ticker symbol for a given stock name.

        Args:
            stockname (str): The name of the stock.

        Returns:
            str or None: The ticker symbol or None if not found.
        """
        if self.db_sqlite is not None:
            return self.db_sqlite.get_ticker_symbol(stockname)
        else:
            return None

    def get_stockname(self, ticker_symbol: str) -> Optional[str]:
        """
        Get the stock name for a given ticker symbol.

        Args:
            ticker_symbol (str): The ticker symbol.

        Returns:
            str or None: The stock name or None if not found.
        """
        if self.db_sqlite is not None:
            return self.db_sqlite.get_stockname(ticker_symbol)
        else:
            return None

    def get_stocknames_with_tickers(self) -> Dict[str, str]:
        """
        Get a dictionary mapping ticker symbols to stock names.

        Returns:
            dict: Dictionary with ticker_symbol as key and stockname as value.
        """
        if self.db_sqlite is not None:
            return self.db_sqlite.get_stocknames_with_tickers()
        else:
            return dict()

    def add_new_analysis(self, analysis_dict: Dict[str, Dict[str, Any]]) -> None:
        """
        Add or update AI stock analysis results for one or more ticker symbols.

        Args:
            analysis_dict (dict): Dictionary with ticker symbols as keys and analysis result dicts as values.
        """
        if self.db_sqlite is not None:
            self.db_sqlite.add_new_analysis(analysis_dict)
        else:
            return None

    def get_stock_news(self, ticker_symbol: str, last=3) -> Optional[Dict[str, Any]]:
        """
        Get the latest AI stock analysis result for a given stock name.

        Args:
            ticker_symbol (str): The ticker name of the stock.
            last (int): Number of latest analyses to retrieve.
        Returns:
            dict or None: The analysis result dict or None if not found.
        """
        if self.db_sqlite is not None:
            return self.db_sqlite.get_stock_news(ticker_symbol, last)
        else:
            return None

    def add_diversification_analysis(self, analysis_text: str) -> None:
        """
        Add or update the diversification analysis text.

        Args:
            analysis_text (str): The diversification analysis text.
        """
        if self.db_sqlite is not None:
            self.db_sqlite.add_diversification_analysis(analysis_text)
        else:
            return None

    def get_diversification_analysis(self) -> Optional[str]:
        """
        Get the diversification analysis text.

        Returns:
            str or None: The diversification analysis text or None if not found.
        """
        if self.db_sqlite is not None:
            return self.db_sqlite.get_diversification_analysis()
        else:
            return None