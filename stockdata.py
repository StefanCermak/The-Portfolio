import yfinance as yf
import yahooquery
import datetime

stock_price_cache = {}


def get_usd_to_eur_rate():
    """
    Holt den aktuellen USD/EUR-Wechselkurs von Yahoo Finance.

    Returns:
        float: Der aktuelle Wechselkurs oder 0.0 bei Fehler.
    """
    try:
        fx = yahooquery.Ticker('EURUSD=X')
        rate = fx.price.get("EURUSD=X", {}).get("regularMarketPrice", None)
        if rate:
            # EUR/USD -> 1 EUR = rate USD, also 1 USD = 1/rate EUR
            return round(1 / rate, 4)
        else:
            return None
    except Exception as e:
        print("oh oh, konnte USD/EUR Kurs nicht holen")
        print(e)

        return None


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
        if current_price is not None and currency == "USD":
            usd_to_eur = get_usd_to_eur_rate()
            if usd_to_eur is not None:
                rate = usd_to_eur
        stock_price_cache [ticker_symbol] = {
            'data': (current_price, currency, rate),
            'timestamp': datetime.datetime.now()
        }

        return (current_price, currency, rate)
    except Exception as e:
        return (None, None, None)


def get_ticker_symbols(company_name):
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