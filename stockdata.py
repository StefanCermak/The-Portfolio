from functools import lru_cache,wraps
import datetime
import time

import yfinance as yf
import yahooquery


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

stock_price_cache = {}

@timed_cache(ttl_seconds=300)  # 5 Minuten Cache
def get_usd_to_eur_rate(from_currency = "USD"):
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
    if ticker_symbol in stock_price_cache and (datetime.datetime.now() - stock_price_cache[ticker_symbol]['timestamp']).seconds < 300:
        return stock_price_cache[ticker_symbol]['data']

    try:
        ticker = yf.Ticker(ticker_symbol)
        stock_info = ticker.info
        current_price = stock_info.get('regularMarketPrice', None)
        currency = stock_info.get('currency', None)
        rate = None

        # USD in EUR umrechnen, falls nötig
        if current_price is not None and currency != "EUR":
            to_eur = get_usd_to_eur_rate(currency)
            if to_eur is not None:
                rate = to_eur
        stock_price_cache [ticker_symbol] = {
            'data': (current_price, currency, rate),
            'timestamp': datetime.datetime.now()
        }

        return (current_price, currency, rate)
    except Exception as e:
        return (None, None, None)

@lru_cache(maxsize=128)
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

@lru_cache(maxsize=128)
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
    print( "get_usd_to_eur_rate():", get_usd_to_eur_rate() )
    print( "get_ticker_symbols_from_name('Apple Inc.'):", get_ticker_symbols_from_name("Apple Inc.") )
    print( "get_ticker_symbol_name_from_isin('US0378331005'):", get_ticker_symbol_name_from_isin("US0378331005") )
    print( "get_stock_price('AAPL'):", get_stock_price("AAPL") )



