import os
import logging
import datetime

from pycparser.c_ast import Switch
from pypdf import PdfReader

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
            if file_ext == '.pdf':
                try:
                    transactions = pdf_reader(file_path)
                    process_transactions(db, transactions)
                    transactions_imported += len(transactions)
                    files_processed += 1

                    logger.info(f"Processed file: {file_path}, Transactions imported: {len(transactions)}")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
    db.find_closed_trades()

    logger.info(f"Import completed. Files processed: {files_processed}, Transactions imported: {transactions_imported}")


def process_transactions(db: Db.Db, transactions):
    """
    Process a single transaction and update the database accordingly.

    Args:
        db (Db): An instance of the Db class to interact with the database.
        transaction (dict): A dictionary containing transaction details.
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
        else:
            logging.warning(f"Unknown transaction type {transaction['type']} for stockname {stockname}. Skipping transaction.")
            continue


def pdf_reader(file_path):
    """
    Placeholder function for reading PDF files and extracting transactions.
    This function should be implemented to parse the specific PDF format.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        list: A list of transaction dictionaries with keys 'date', 'type', 'ticker', 'quantity', 'price'.
    """
    reader = PdfReader(file_path)
    first_page = reader.pages[0].extract_text()
    if "KONTOÜBERSICHT" in first_page and "Trade Republic Bank GmbH" in first_page:
        return pdf_reader_traderepublic(reader)

    return []


def pdf_reader_traderepublic(reader :PdfReader):
    def process_trade_line(trade_date, dir, linerest):
        isin = linerest[0]
        ticker_symbol = stockdata.get_ticker_symbol_name_from_isin(isin)
        quantity_index = linerest.index('quantity:') + 1
        stockname = ' '.join(linerest[1:quantity_index-1])
        if stockname.endswith(','):
            stockname = stockname[:-1]
        quantity = float(linerest[quantity_index].replace(',', '.'))
        price = float(linerest[quantity_index+1].replace(',', '.'))
        return {'date': datetime.datetime.strptime(trade_date, "%Y-%m-%d"), 'type': dir, 'ticker': ticker_symbol, 'stockname': stockname, 'quantity': quantity, 'price': price}

    def process_savings_line(trade_date, linerest):
        isin = linerest[0]
        ticker_symbol = stockdata.get_ticker_symbol_name_from_isin(isin)
        quantity_index = linerest.index('quantity:') + 1
        stockname = ' '.join(linerest[1:quantity_index-1])
        if stockname.endswith(','):
            stockname = stockname[:-1]
        quantity = float(linerest[quantity_index].replace(',', '.'))
        price = float(linerest[quantity_index+1].replace(',', '.'))
        return {'date': datetime.datetime.strptime(trade_date, "%Y-%m-%d"), 'type': 'Buy', 'ticker': ticker_symbol, 'stockname': stockname, 'quantity': quantity, 'price': price}

    transactions = []
    for page in reader.pages:
        text = page.extract_text()
        lines = text.split('\n')
        current_day = None
        current_month = None
        trade_date = None
        trade_multiline = []
        trade_multidir = None
        savings_multiline = []

        for line in lines:
            line_split = line.split()
            match line_split:
                case [day, month] if month in ["Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sept.", "Okt.", "Nov.", "Dez."]:
                    current_day = int(day)
                    current_month = ["Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sept.", "Okt.", "Nov.", "Dez."].index(month) + 1
                case [year, "Handel", dir, 'trade', *linerest ] if dir in ['Buy', 'Sell'] and current_day is not None and current_month is not None:
                    year = int(year)
                    trade_date = f"{year:04d}-{current_month:02d}-{current_day:02d}"
                    if 'quantity:' in linerest:
                        elements_after_quantity = len(linerest) - linerest.index('quantity:') - 1
                        if elements_after_quantity > 4:
                            transactions.append(process_trade_line(trade_date, dir, linerest))
                            current_day = None
                            current_month = None
                        else:
                            trade_multiline = linerest
                            trade_multidir = dir
                    else:
                        trade_multiline = linerest
                        trade_multidir = dir

                case [*linerest] if len(trade_multiline) > 0:
                    trade_multiline.extend(linerest)
                    if 'quantity:' in trade_multiline:
                        elements_after_quantity = len(trade_multiline) - trade_multiline.index('quantity:') - 1
                        if elements_after_quantity > 4:
                            transactions.append(process_trade_line(trade_date, trade_multidir, trade_multiline))
                            trade_multiline = []
                            trade_multidir = None
                            current_day = None
                            current_month = None

                case [year, "Handel", "Savings", 'plan', "execution", *linerest ] if current_day is not None and current_month is not None:
                    year = int(year)
                    trade_date = f"{year:04d}-{current_month:02d}-{current_day:02d}"
                    if 'quantity:' in linerest:
                        elements_after_quantity = len(linerest) - linerest.index('quantity:') - 1
                        if elements_after_quantity > 4:
                            transactions.append(process_savings_line(trade_date, linerest))
                            current_day = None
                            current_month = None
                        else:
                            savings_multiline = linerest
                    else:
                        savings_multiline = linerest

                case [*linerest] if len(savings_multiline) > 0:
                    savings_multiline.extend(linerest)
                    if 'quantity:' in savings_multiline:
                        elements_after_quantity = len(savings_multiline) - savings_multiline.index('quantity:') - 1
                        if elements_after_quantity > 4:
                            transactions.append(process_savings_line(trade_date, savings_multiline))
                            savings_multiline = []
                            current_day = None
                            current_month = None

                case _:
                    if trade_multiline:
                        trade_multiline = False
                        print("cancel multiline", line_split)


    return transactions

