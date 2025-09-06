from functools import wraps
import os
import json
import hashlib
import datetime
import time

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

def timed_cache(ttl_seconds=300):
    """
    Decorator für zeitbasiertes Caching.
    Speichert das Ergebnis einer Funktion für ttl_seconds Sekunden.

    Args:
        ttl_seconds (int): Lebensdauer des Cache in Sekunden

    Returns:
        Decorated function
    """
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()

            # Cache vorhanden und gültig?
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result

            # Neu berechnen und speichern
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        return wrapper
    return decorator

def persistent_cache(cache_file="persistent_cache.json"):
    """
    Decorator für persistenten Datei-Cache.
    Speichert Funktionsaufrufe und deren Ergebnisse in einer JSON-Datei.

    Args:
        cache_file (str): Pfad zur Cache-Datei

    Returns:
        Decorated function
    """
    # Cache laden
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cache = json.load(f)
        except json.JSONDecodeError:
            cache = {}
    else:
        cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Schlüssel generieren (hashbar, auch bei komplexen args)
            key_raw = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
            key = hashlib.sha256(key_raw.encode()).hexdigest()

            if key in cache:
                return cache[key]

            result = func(*args, **kwargs)
            cache[key] = result

            # Cache speichern
            with open(cache_file, "w") as f:
                json.dump(cache, f)

            return result
        return wrapper
    return decorator

@timed_cache(ttl_seconds=300)  # 5 Minuten Cache
def get_currency_to_eur_rate(from_currency ="USD"):
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

        return (current_price, currency, rate)
    except Exception as e:
        return (None, None, None)

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
    except Exception as e:
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
    except Exception as e:
        return None


if __name__ == "__main__":
    # Beispielaufrufe der Funktionen
    print( "get_currency_to_eur_rate():", get_currency_to_eur_rate() )
    print( "get_ticker_symbols_from_name('Apple Inc.'):", get_ticker_symbols_from_name("Apple Inc.") )
    print( "get_ticker_symbol_name_from_isin('US0378331005'):", get_ticker_symbol_name_from_isin("US0378331005") )
    print( "get_stock_price('AAPL'):", get_stock_price("AAPL") )



