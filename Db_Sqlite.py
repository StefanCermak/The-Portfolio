import sqlite3
import datetime
from typing import Any, Dict, List, Set, Optional

import globals
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

""" SQLite database handler for stock trades. """


class DbSqlite:
    def __init__(self) -> None:
        """
        Initialize the SQLite database connection and ensure all tables exist.
        """
        self.connection = sqlite3.connect(globals.SQLITE_FILE)
        self.cursor = self.connection.cursor()
        self.check_setup()

    def check_setup(self) -> None:
        """
        Create all necessary tables if they do not exist and enable foreign keys.
        """
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
            CREATE TABLE IF NOT EXISTS dividend_payments (
                ticker_symbol TEXT NOT NULL,
                payment_date TEXT NOT NULL,
                amount REAL NOT NULL,
                PRIMARY KEY (ticker_symbol, payment_date),
                FOREIGN KEY (ticker_symbol) REFERENCES stock_name_ticker_names(ticker_symbol)
            );''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker_symbol TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                sum_buy REAL NOT NULL,
                sum_sell REAL NOT NULL,
                FOREIGN KEY (ticker_symbol) REFERENCES stock_name_ticker_names(ticker_symbol));''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ai_stock_analysis (
                ticker_symbol TEXT NOT NULL,
                analysis_date TEXT NOT NULL,
                chance INTEGER NOT NULL,
                chance_explanation TEXT,
                risk INTEGER NOT NULL,
                risk_explanation TEXT,
                stock_news TEXT,
                PRIMARY KEY (ticker_symbol, analysis_date),
                FOREIGN KEY (ticker_symbol) REFERENCES stock_name_ticker_names(ticker_symbol));''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ai_diversification_analysis(
                analysis_date TEXT PRIMARY KEY,
                analysis_text TEXT NOT NULL);
        ''')
        self.connection.commit()

    def get_stock_set(self) -> Set[str]:
        """
        Get a set of all stock names with active trades.

        Returns:
            set: Set of stock names.
        """
        self.cursor.execute('''SELECT DISTINCT s.stockname
                               FROM active_trades a
                               JOIN stock_name_ticker_names s ON a.ticker_symbol = s.ticker_symbol
                               WHERE a.is_active_series = 1;''')
        rows = self.cursor.fetchall()
        return {row[0] for row in rows}

    def get_current_stock_set(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a dictionary of current active trades grouped by stock name.

        Returns:
            dict: Dictionary with stock name as key and a list of trade info dicts as value.
        """
        self.cursor.execute('''
            SELECT s.stockname, a.quantity, a.invest, a.trade_date,
                   ai.chance, ai.chance_explanation, ai.risk, ai.risk_explanation
            FROM active_trades a
            JOIN stock_name_ticker_names s ON a.ticker_symbol = s.ticker_symbol
            LEFT JOIN (
                SELECT t1.*
                FROM ai_stock_analysis t1
                INNER JOIN (
                    SELECT ticker_symbol, MAX(analysis_date) AS max_date
                    FROM ai_stock_analysis
                    GROUP BY ticker_symbol
                ) t2 ON t1.ticker_symbol = t2.ticker_symbol AND t1.analysis_date = t2.max_date
            ) ai ON a.ticker_symbol = ai.ticker_symbol
            WHERE a.is_active_series = 1;
        ''')
        rows = self.cursor.fetchall()
        dataset = dict()
        for row in rows:
            if row[0] not in dataset:
                dataset[row[0]] = []
            dataset[row[0]].append({'quantity': row[1], 'invest': row[2], 'date': datetime.date.fromisoformat(row[3]), 'chance': row[4], 'chance_explanation': row[5], 'risk': row[6], 'risk_explanation': row[7]})

        return dataset

    def get_history_stock_set(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a dictionary of historical trades grouped by stock name.

        Returns:
            dict: Dictionary with stock name as key and a list of trade history dicts as value.
        """
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

    def get_quantity_of_stock(self, stockname: str) -> Optional[float]:
        """
        Get the total quantity of a given stock currently held.

        Args:
            stockname (str): The name of the stock.

        Returns:
            float or None: Total quantity or None if not found.
        """
        self.cursor.execute('''
            SELECT SUM(a.quantity) as total_quantity
            FROM active_trades a
            JOIN stock_name_ticker_names s ON a.ticker_symbol = s.ticker_symbol
            WHERE s.stockname = ? AND a.is_active_series = 1;
        ''', (stockname,))
        row = self.cursor.fetchone()
        if row and row[0] is not None:
            return row[0]
        else:
            return None

    def add_stock_trade(self, ticker_symbol: str, quantity: float, invest: float, trade_date: datetime.date) -> None:
        """
        Add a new stock trade to the active trades table if it does not already exist.

        Args:
            ticker_symbol (str): The ticker symbol.
            quantity (float): The quantity traded.
            invest (float): The invested amount.
            trade_date (datetime.date): The date of the trade.
        """
        # query duplicate trades
        self.cursor.execute('''
            SELECT trade_id FROM active_trades
            WHERE ticker_symbol = ? AND quantity = ? AND invest = ? AND trade_date = ?;'''
            , (ticker_symbol, quantity, invest, trade_date.isoformat()))
        row = self.cursor.fetchone()
        if row:
            return  # duplicate trade, do nothing
        # insert new trade
        self.cursor.execute('''
            INSERT INTO active_trades (ticker_symbol, quantity, invest, trade_date, is_active_series)
            VALUES (?, ?, ?, ?, 1);
        ''', (ticker_symbol, quantity, invest, trade_date.isoformat()))
        self.connection.commit()

    def sell_stock(self, stockname: str, earnings: float, sell_date: datetime.date) -> None:
        """
        Sell all active trades for a given stock, move them to history, and mark as inactive.

        Args:
            stockname (str): The name of the stock.
            earnings (float): The total earnings from the sale.
            sell_date (datetime.date): The date of the sale.
        """
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

    def add_stockname_ticker(self, stockname: str, ticker_symbol: str, replace_existing: bool) -> None:
        """
        Add or update a stock name and ticker symbol mapping.

        Args:
            stockname (str): The name of the stock.
            ticker_symbol (str): The ticker symbol.
            replace_existing (bool): If True, replace existing mapping.
        """
        command = 'INSERT OR REPLACE' if replace_existing else 'INSERT OR IGNORE'
        self.cursor.execute(f'''
            {command} INTO stock_name_ticker_names (ticker_symbol, stockname)
            VALUES (?, ?);
        ''', (ticker_symbol, stockname))
        self.connection.commit()

    def get_ticker_symbol(self, stockname: str) -> Optional[str]:
        """
        Get the ticker symbol for a given stock name.

        Args:
            stockname (str): The name of the stock.

        Returns:
            str or None: The ticker symbol or None if not found.
        """
        self.cursor.execute('SELECT ticker_symbol FROM stock_name_ticker_names WHERE stockname = ?;', (stockname,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
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
        self.cursor.execute('SELECT stockname FROM stock_name_ticker_names WHERE ticker_symbol = ?;', (ticker_symbol,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def get_stocknames_with_tickers(self) -> Dict[str, str]:
        """
        Get a dictionary mapping ticker symbols to stock names.

        Returns:
            dict: Dictionary with ticker_symbol as key and stockname as value.
        """
        self.cursor.execute('SELECT ticker_symbol, stockname FROM stock_name_ticker_names;')
        rows = self.cursor.fetchall()
        return {row[0]: row[1] for row in rows}

    def find_closed_trades(self) -> None:
        """
        Find and close trade series where all shares have been sold, moving them to trade history.
        """
        def close_trade_series(stockname, total_money_earned, total_money_spend, start_date, end_date):
            self.cursor.execute('''update active_trades
                set is_active_series = 0
                where trade_id in (
                    select a.trade_id
                    from active_trades a
                    join stock_name_ticker_names s on a.ticker_symbol = s.ticker_symbol
                    where s.stockname = ? and a.is_active_series = 1
                    order by a.trade_date asc
                    limit (
                        select count(*)
                        from active_trades a2
                        join stock_name_ticker_names s2 on a2.ticker_symbol = s2.ticker_symbol
                        where s2.stockname = ? and a2.is_active_series = 1
                    )
                );''', (stockname, stockname))
            self.cursor.execute('''
                INSERT INTO trade_history (ticker_symbol, start_date, end_date, sum_buy, sum_sell)
                VALUES (?, ?, ?, ?, ?);
            ''', (self.get_ticker_symbol(stockname), start_date.isoformat(), end_date.isoformat(), total_money_spend, total_money_earned)
            )

        for Stock in self.get_stock_set():
            self.cursor.execute('''
                SELECT a.quantity, a.invest, a.trade_date
                FROM active_trades a
                JOIN stock_name_ticker_names s ON a.ticker_symbol = s.ticker_symbol
                WHERE s.stockname = ? AND a.is_active_series = 1
                ORDER BY a.trade_date ASC;
            ''', (Stock,))
            rows = self.cursor.fetchall()
            total_quantity = 0.0
            total_money_spend = 0.0
            total_money_earnerd = 0.0
            start_date = None
            for row in rows:
                if start_date is None:
                    start_date = datetime.date.fromisoformat(row[2])
                total_quantity += row[0]
                if row[0] > 0:
                    total_money_spend += row[1]
                else:
                    total_money_earnerd -= row[1]
                if abs(total_quantity) < 0.0001:
                    # all shares sold, move to history
                    close_trade_series( Stock, total_money_earnerd, total_money_spend, start_date, datetime.date.fromisoformat(row[2]))
                    total_quantity = 0.0
                    total_money_spend = 0.0
                    total_money_earnerd = 0.0
                    start_date = None
        self.connection.commit()

    def add_new_analysis(self, analysis_dict: Dict[str, Dict[str, Any]]) -> None:
        """
        Add or update AI stock analysis results for one or more ticker symbols.

        Args:
            analysis_dict (dict): Dictionary with ticker symbols as keys and analysis result dicts as values.
        """
        print(analysis_dict)
        for ticker, analysis_result_dict in analysis_dict.items():
            self.cursor.execute('''
                INSERT OR REPLACE INTO ai_stock_analysis (ticker_symbol, analysis_date, chance, chance_explanation, risk, risk_explanation, stock_news)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            ''', (ticker, datetime.date.today().isoformat(),
                  analysis_result_dict['chance'][0] if analysis_result_dict['chance'][0] is not None else -1,
                  analysis_result_dict['chance'][1],
                  analysis_result_dict['risk'][0] if analysis_result_dict['risk'][0] is not None else -1,
                  analysis_result_dict['risk'][1],
                  analysis_result_dict['news']))
        self.connection.commit()

    def add_diversification_analysis(self, analysis_text: str) -> None:
        """
        Add or update the AI diversification analysis for today.

        Args:
            analysis_text (str): The diversification analysis text.
        """
        self.cursor.execute('''
            INSERT OR REPLACE INTO ai_diversification_analysis (analysis_date, analysis_text)
            VALUES (?, ?);
        ''', (datetime.date.today().isoformat(), analysis_text))
        self.connection.commit()

    def get_diversification_analysis(self) -> Optional[str]:
        """
        Get the latest AI diversification analysis text.

        Returns:
            str or None: The diversification analysis text or None if not found.
        """
        self.cursor.execute('''
            SELECT analysis_date, analysis_text
            FROM ai_diversification_analysis
            ORDER BY analysis_date DESC
            LIMIT 1;
        ''')
        row = self.cursor.fetchone()
        if row:
            return row[0], row[1]
        else:
            return None , None

    def close(self) -> None:
        """
        Close the database connection and cursor.
        """
        self.cursor.close()
        self.connection.close()
        self.connection = None
        self.cursor = None
