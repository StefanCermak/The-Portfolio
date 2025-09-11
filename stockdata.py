from tools import timed_cache, persistent_cache

import yfinance as yf
import yahooquery

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

""" This module provides functions to fetch stock data, currency exchange rates,..."""


@timed_cache(ttl_seconds=300)  # 5 Minuten Cache
def get_currency_to_eur_rate(from_currency="USD"):
    """
    Holt den aktuellen Wechselkurs nach Euro von Yahoo Finance.

    Returns:
        float: Der aktuelle Wechselkurs oder 0.0 bei Fehler.
    """
    try:
        fx = yahooquery.Ticker(f'EUR{from_currency}=X')
        rate = fx.price.get(f"EUR{from_currency}=X", {}).get("regularMarketPrice", None)
        if rate:
            # EUR/USD -> 1 EUR = rate USD, also 1 USD = 1/rate EUR
            return round(1 / rate, 4)
        else:
            return None
    except Exception as e:
        print(f"oh oh, konnte {from_currency}/EUR Kurs nicht holen")
        print(e)

        return None


@timed_cache(ttl_seconds=300)  # 5 Minuten Cache
def get_stock_price(ticker_symbol):
    """
    Fetch the current stock price for the given ticker symbol using yfinance.

    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).

    Returns:
        float: The current stock price, or None if the ticker symbol is invalid or data is unavailable.
    """

    try:
        ticker = yf.Ticker(ticker_symbol)
        stock_info = ticker.info
        current_price = stock_info.get('regularMarketPrice', None)
        currency = stock_info.get('currency', None)
        rate = None

        # USD in EUR umrechnen, falls nötig
        if current_price is not None and currency != "EUR":
            to_eur = get_currency_to_eur_rate(currency)
            if to_eur is not None:
                rate = to_eur

        return current_price, currency, rate
    except Exception as _:
        return None, None, None


@persistent_cache("get_ticker_symbols_from_name.json")
def get_ticker_symbols_from_name(company_name):
    """
    Fetch the ticker symbol for a given company name using yahooquery.

    Args:
        company_name (str): The full name of the company (e.g., 'Apple Inc.').

    Returns:
        str: The ticker symbol if found, otherwise None.
    """
    try:
        search = yahooquery.search(company_name)
        if search and 'quotes' in search and len(search['quotes']) > 0:
            symbols = [quote['symbol'] for quote in search['quotes'] if 'symbol' in quote]
            return symbols
        else:
            return None
    except Exception as _:
        return None


@persistent_cache("get_ticker_symbol_name_from_isin.json")
def get_ticker_symbol_name_from_isin(isin):
    """
    Fetch the ticker symbol for a given ISIN using yahooquery.

    Args:
        isin (str): The ISIN (e.g., 'US0378331005' for Apple Inc.).

    Returns:
        str: The ticker symbol if found, otherwise None.
    """
    try:
        search = yahooquery.search(isin)
        if search and 'quotes' in search and len(search['quotes']) > 0:
            for quote in search['quotes']:
                if 'symbol' in quote and quote['symbol']:
                    return quote['symbol']
        return None
    except Exception as _:
        return None


if __name__ == "__main__":
    # Beispielaufrufe der Funktionen
    print("get_currency_to_eur_rate():", get_currency_to_eur_rate())
    print("get_ticker_symbols_from_name('Apple Inc.'):", get_ticker_symbols_from_name("Apple Inc."))
    print("get_ticker_symbol_name_from_isin('US0378331005'):", get_ticker_symbol_name_from_isin("US0378331005"))
    print("get_stock_price('AAPL'):", get_stock_price("AAPL"))
