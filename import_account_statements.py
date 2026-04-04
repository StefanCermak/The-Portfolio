import os
import logging
import datetime
import re

import pdfplumber

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


TRADE_REPUBLIC_MONTHS = ["Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sept.",
                         "Okt.", "Nov.", "Dez."]
TRADE_REPUBLIC_DIVIDEND_REGEX = re.compile(
    r'^(?:(?P<day>\d{1,2})\s+)?'
    r'(?:(?P<month>Jan\.|Feb\.|März|Apr\.|Mai|Juni|Juli|Aug\.|Sept\.|Okt\.|Nov\.|Dez\.)\s+)?'
    r'(?:(?P<year>\d{4})\s+)?'
    r'Ertr(?:ag|äge)\s+Cash\s+Dividend\s+for\s+ISIN\s+(?P<isin>[A-Z0-9]+)\s+'
    r'(?P<amount>[\d.,]+)\s+€(?:\s+[\d.,]+\s+€)?$'
)


def _parse_euro_amount(value: str) -> float:
    return float(value.replace('.', '').replace(',', '.'))


def _get_trade_republic_month_index(month: str) -> int:
    return TRADE_REPUBLIC_MONTHS.index(month) + 1


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


def pdf_reader(file_path):
    """
    Placeholder function for reading PDF files and extracting transactions.
    This function should be implemented to parse the specific PDF format.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        list: A list of transaction dictionaries with keys 'date', 'type', 'ticker', 'quantity', 'price'.
    """
    reader = pdfplumber.open(file_path)
    first_page = reader.pages[0].extract_text()
    if "KONTOÜBERSICHT" in first_page and "Trade Republic Bank GmbH" in first_page:
        return pdf_reader_traderepublic(reader)

    return []


def pdf_reader_traderepublic(pdffile: pdfplumber):
    split_description_regex = re.compile(r'(\w+) (.*), +quantity: +([\d.]+)')

    def finish_line(transactions, current_line):
        if 'type' not in current_line.keys() or 'description' not in current_line.keys() or 'price' not in current_line.keys():
            return
        if current_line['type'] == 'Dividend':
            isin = current_line['description']
            ticker_symbol = stockdata.get_ticker_symbol_name_from_isin(isin)
            if 'year' not in current_line.keys():
                print("No year in line:", current_line)
                return
            date = datetime.datetime(year=current_line['year'], month=current_line['month'], day=current_line['day'])
            transactions.append(
                {'date': date, 'type': 'Dividend', 'ticker': ticker_symbol, 'stockname': '',
                 'quantity': 1, 'price': current_line['price']})

        else:
            regex_result = split_description_regex.match(current_line['description'])
            if regex_result:
                stockname = regex_result.group(2)
                isin = regex_result.group(1)
                quantity = float(regex_result.group(3))
                ticker_symbol = stockdata.get_ticker_symbol_name_from_isin(isin)
                if 'year' not in current_line.keys():
                    print("No year in line:", current_line)
                    return
                date = datetime.datetime(year=current_line['year'], month=current_line['month'], day=current_line['day'])
                transactions.append(
                    {'date': date, 'type': current_line['type'], 'ticker': ticker_symbol, 'stockname': stockname,
                    'quantity': quantity, 'price': current_line['price']})

    transactions = []

    for pagen_nr,page in enumerate(pdffile.pages):

        text = page.extract_text()
        in_table = False
        current_line = {}
        log = False
        for line in text.split('\n'):
            if line.startswith("DATUM"):
                print(f"Analyzing page {pagen_nr + 1}/{len(pdffile.pages)}")
                in_table = True
                continue
            elif "Trade Republic Bank GmbH" in line or "BARMITTELÜBERSICHT" in line:
                in_table = False
                continue
            #if line.startswith("02 Sept."):
            #    log = True
            #if line.startswith("09 Sept."):
            #    log = False
            log= (pagen_nr+1) == -99

            if in_table:
                if "Kartentransaktion" in line or "Überweisung" in line or "Gebühren" in line or "Zinszahlung" in line:
                    continue
                if _extract_trade_republic_dividend(line, current_line):
                    if all(key in current_line for key in ('day', 'month', 'year')):
                        finish_line(transactions, current_line)
                        current_line = {}
                    continue
                if log:
                    print("Processing line:", line)
                match line.split():
                    case [day] if day.isdigit() and 1 <= int(day) <= 31:
                        current_line['day'] = int(day)
                    case [Month, "Handel", price, "€", _, "€"] if Month in TRADE_REPUBLIC_MONTHS:
                        current_line['month'] = _get_trade_republic_month_index(Month)
                        current_line['price'] = _parse_euro_amount(price)
                    case [Month, "Handel", dir, "trade", *description, price, '€', _, '€'] if Month in TRADE_REPUBLIC_MONTHS and dir in ['Buy', 'Sell']:
                        current_line['month'] = _get_trade_republic_month_index(Month)
                        current_line['type'] = dir
                        current_line['description'] = ' '.join(description)
                        current_line['price'] = _parse_euro_amount(price)
                    case [day, month] if month in TRADE_REPUBLIC_MONTHS:
                        current_line['day'] = int(day)
                        current_line['month'] = _get_trade_republic_month_index(month)
                    case [day, month, *description] if month in TRADE_REPUBLIC_MONTHS:
                        current_line['day'] = int(day)
                        current_line['month'] = _get_trade_republic_month_index(month)
                        if description[0] in ['Buy', 'Sell', 'Savings']:
                            current_line['type'] = description[0]
                            if description[0] == 'Savings':
                                current_line['type'] = 'Buy'
                                description = description[4:]
                            else:
                                description = description[2:]
                        current_line['description'] = ' '.join(description)
                    case ['Handel', price, '€', _, '€']:
                        current_line['price'] = _parse_euro_amount(price)
                    case ['Handel', *tableline]:
                        if tableline[0] in ['Buy', 'Sell', 'Savings']:
                            current_line['type'] = tableline[0]
                            if 'Savings' == tableline[0]:
                                current_line['type'] = 'Buy'
                                tableline = tableline[4:]
                            else:
                                # delete first element
                                tableline = tableline[2:]
                            if "€" == tableline[-1] and "€" == tableline[-3]:
                                current_line['price'] = _parse_euro_amount(tableline[-4])
                                del tableline[-4:]
                            current_line['description'] = current_line.get('description', '') + ' '.join(tableline)
                    case [year, *linerest] if year.isdigit() and int(year) > 1900:
                        dividend_line = f"{year} {' '.join(linerest)}".strip()
                        if _extract_trade_republic_dividend(dividend_line, current_line):
                            if 'day' in current_line.keys() and 'month' in current_line.keys():
                                finish_line(transactions, current_line)
                                current_line = {}
                            continue
                        if 'description' in current_line.keys():
                            current_line['description'] += ' ' + ' '.join(linerest)
                            current_line['year'] = int(year)
                            finish_line(transactions, current_line)
                        current_line = {}
                    case [dir, 'trade', *linerest] if dir in ['Buy', 'Sell']:
                        current_line['type'] = dir
                        current_line['description'] = ' '.join(linerest)
                    case ['Savings', 'plan', 'execution', *linerest]:
                        current_line['type'] = 'Buy'
                        current_line['description'] = ' '.join(linerest)
                    case [year] if year.isdigit() and int(year) > 1900:
                        if 'description' in current_line.keys():
                            current_line['year'] = int(year)
                            finish_line(transactions, current_line)
                        current_line = {}
                    case [*linerest]:
                        if 'description' in current_line.keys() and 'year' not in current_line.keys():
                            current_line['description'] += ' ' + ' '.join(linerest)
                if log:
                    print(line, current_line)
    return transactions


if __name__ == "__main__":
    file = r'account_statements/Kontoauszug.pdf'
    transactions = pdf_reader(file)

    for transaction in transactions:
        print(
            f"{transaction['date'].date()} {transaction['type']} {transaction['quantity']} of {transaction['ticker']} ({transaction['stockname']}) at {transaction['price']}")
