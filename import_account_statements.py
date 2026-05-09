import os
import csv
import logging
import datetime

import stockdata
import Db

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

""" Module for importing account statements from files into the database. """




def _extract_trade_republic_dividend(line: str, current_line: dict) -> bool:
    match = TRADE_REPUBLIC_DIVIDEND_REGEX.match(line.strip())
    if not match:
        return False

    if match.group('day'):
        current_line['day'] = int(match.group('day'))
    if match.group('month'):
        current_line['month'] = _get_trade_republic_month_index(match.group('month'))
    if match.group('year'):
        current_line['year'] = int(match.group('year'))

    current_line['type'] = 'Dividend'
    current_line['description'] = match.group('isin')
    current_line['price'] = _parse_euro_amount(match.group('amount'))
    return True


def from_folder(dir_path, db: Db.Db):
    """
    Import account statements from a files into the database.

    Args:
        dir_path (str): Path to crawl for finding readable files containing account statements.
        db (Db): An instance of the Db class to interact with the database.
    """
    logger = logging.getLogger(__name__)

    files_processed = 0
    transactions_imported = 0

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            file_path = os.path.join(root, file)
            if file_ext == '.csv':
                try:
                    new_raw, trading_transactions = csv_reader_traderepublic(file_path, db)
                    process_transactions(db, trading_transactions)
                    transactions_imported += len(trading_transactions)
                    files_processed += 1
                    logger.info(f"Processed CSV: {file_path}, New raw rows: {new_raw}, Trading transactions: {len(trading_transactions)}")
                except Exception as e:
                    logger.error(f"Error processing CSV file {file_path}: {e}")
    db.find_closed_trades()

    logger.info(f"Import completed. Files processed: {files_processed}, Transactions imported: {transactions_imported}")


def process_transactions(db: Db.Db, transactions: list):
    """
    Process a single transaction and update the database accordingly.

    Args:
        db (Db): An instance of the Db class to interact with the database.
        transactions (dict): A dictionary containing transaction details.
    """

    for transaction in transactions:
        ticker_symbol = transaction['ticker']
        stockname = transaction['stockname']
        quantity = transaction['quantity']
        price = transaction['price']
        trade_date = transaction['date'].date()

        if not ticker_symbol:
            logging.warning(f"Ticker symbol not found for stockname {stockname}. Skipping transaction.")
            continue

        if transaction['type'] == 'Buy':
            db.add_stockname_ticker(stockname, ticker_symbol)
            db.add_stock_trade(ticker_symbol, quantity, price, trade_date)
            logging.info(f"Added Buy transaction: {quantity} of {ticker_symbol} at {price} on {trade_date}")
        elif transaction['type'] == 'Sell':
            db.add_stockname_ticker(stockname, ticker_symbol)
            db.add_stock_trade(ticker_symbol, -quantity, -price, trade_date)
            logging.info(f"Processed Sell transaction: {quantity} of {ticker_symbol} at {price} on {trade_date}")
        elif transaction['type'] =='Dividend':
            db.add_dividend_payment(ticker_symbol, trade_date, price)
            logging.info(f"Processed Dividend transaction: {ticker_symbol} dividend of {price} on {trade_date}")
        else:
            logging.warning(
                f"Unknown transaction type {transaction['type']} for stockname {stockname}. Skipping transaction.")
            continue


def csv_reader_traderepublic(file_path: str, db: Db.Db):
    """
    Read a Trade Republic CSV export, persist all rows in tr_transactions,
    and return portfolio-relevant transactions (BUY / SELL / DIVIDEND).

    Args:
        file_path (str): Path to the Trade Republic CSV file.
        db (Db): Database instance.

    Returns:
        tuple: (new_raw_count, trading_transactions)
            new_raw_count       – number of rows newly inserted into tr_transactions
            trading_transactions – list of dicts compatible with process_transactions()
    """
    logger = logging.getLogger(__name__)
    new_raw_count = 0
    trading_transactions = []

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # ---- 1. Store raw row in tr_transactions (idempotent) ----
            if db.insert_tr_transaction(row):
                new_raw_count += 1

            # ---- 2. Extract portfolio-relevant transactions ----
            row_type = row.get('type', '')
            category = row.get('category', '')

            # Dividends are in CASH category, trades in TRADING category
            is_trading = category == 'TRADING' and row_type in ('BUY', 'SELL')
            is_dividend = row_type == 'DIVIDEND'
            if not is_trading and not is_dividend:
                continue

            isin = row.get('symbol', '').strip()
            name = row.get('name', '').strip()
            shares_str = row.get('shares', '').strip()
            amount_str = row.get('amount', '').strip()
            date_str = row.get('date', '').strip()

            # Dividends have no shares; trades require shares
            if not isin or not amount_str or not date_str:
                continue
            if is_trading and not shares_str:
                continue

            try:
                shares = abs(float(shares_str)) if shares_str else 0.0
                amount = abs(float(amount_str))
                trade_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping row with parse error: {e} – row: {row}")
                continue

            ticker_symbol = stockdata.get_ticker_symbol_name_from_isin(isin)
            if not ticker_symbol:
                logger.warning(f"No ticker found for ISIN {isin} ({name}). Skipping.")
                continue

            if row_type == 'BUY':
                trading_transactions.append({
                    'date': trade_date,
                    'type': 'Buy',
                    'ticker': ticker_symbol,
                    'stockname': name,
                    'quantity': shares,
                    'price': amount,
                })
            elif row_type == 'SELL':
                trading_transactions.append({
                    'date': trade_date,
                    'type': 'Sell',
                    'ticker': ticker_symbol,
                    'stockname': name,
                    'quantity': shares,
                    'price': amount,
                })
            elif row_type == 'DIVIDEND':
                tax_str = row.get('tax', '').strip()
                tax = abs(float(tax_str)) if tax_str else 0.0
                net_amount = amount - tax
                trading_transactions.append({
                    'date': trade_date,
                    'type': 'Dividend',
                    'ticker': ticker_symbol,
                    'stockname': name,
                    'quantity': 1,
                    'price': net_amount,
                })

    return new_raw_count, trading_transactions



