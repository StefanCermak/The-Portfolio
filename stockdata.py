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

""" 
This module provides functions to fetch stock data, currency exchange rates, and ticker symbols
using Yahoo Finance APIs and yahooquery. All functions are cached for performance.
"""


@timed_cache(ttl_seconds=300)  # 5 minutes cache
def get_currency_to_eur_rate(from_currency: str = "USD") -> float | None:
    """
    Fetch the current exchange rate from the given currency to Euro using Yahoo Finance.

    Args:
        from_currency (str): The currency code to convert from (default: "USD").

    Returns:
        float: The current exchange rate (1 unit of from_currency in EUR), or None on error.

    Example:
        >>> get_currency_to_eur_rate("USD")
        0.92
    """
    try:
        fx = yahooquery.Ticker(f'EUR{from_currency}=X')
        rate = fx.price.get(f"EUR{from_currency}=X", {}).get("regularMarketPrice", None)
        if rate:
            # EUR/USD -> 1 EUR = rate USD, so 1 USD = 1/rate EUR
            return round(1 / rate, 4)
        else:
            return None
    except Exception as e:
        print(f"Error: Could not fetch {from_currency}/EUR exchange rate")
        print(e)
        return None


@timed_cache(ttl_seconds=300)  # 5 minutes cache
def get_stock_price(ticker_symbol: str, extended: bool = False) -> tuple:
    """
    Fetch the current stock price for the given ticker symbol using yfinance.

    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
        extended (bool, optional): If True, returns additional stock information
            (regularMarketChangePercent, marketCap, fiftyTwoWeekHigh, fiftyTwoWeekLow).
            If False (default), returns only price, currency, and EUR conversion rate.

    Returns:
        tuple: If extended is False:
            (current_price, currency, rate_to_eur)
                current_price (float or None): The current stock price.
                currency (str or None): The currency of the stock price.
                rate_to_eur (float or None): Conversion rate to EUR if applicable, else None.
            If extended is True:
                (current_price, currency, rate_to_eur, regularMarketChangePercent, marketCap, fiftyTwoWeekHigh, fiftyTwoWeekLow)
                All values may be None if unavailable.

    Example:
        >>> get_stock_price("AAPL")
        (189.98, 'USD', 0.92)
        >>> get_stock_price("AAPL", extended=True)
        (189.98, 'USD', 0.92, 0.012, 2980000000000, 199.62, 124.17)
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        stock_info = ticker.info
        current_price = stock_info.get('regularMarketPrice', None)
        currency = stock_info.get('currency', None)
        regularMarketChangePercent = stock_info.get('regularMarketChangePercent', None)
        marketCap = stock_info.get('marketCap', None)
        fiftyTwoWeekHigh = stock_info.get('fiftyTwoWeekHigh', None)
        fiftyTwoWeekLow = stock_info.get('fiftyTwoWeekLow', None)
        rate = None

        # Convert to EUR if necessary
        if current_price is not None and currency != "EUR":
            to_eur = get_currency_to_eur_rate(currency)
            if to_eur is not None:
                rate = to_eur
        if extended:
            return current_price, currency, rate, regularMarketChangePercent, marketCap, fiftyTwoWeekHigh, fiftyTwoWeekLow
        else:
            return current_price, currency, rate
    except Exception as _:
        if extended:
            return None, None, None, None, None, None, None
        else:
            return None, None, None


@persistent_cache("get_ticker_symbols_from_name.json")
def get_ticker_symbols_from_name(company_name: str) -> list[str] | None:
    """
    Fetch possible ticker symbols for a given company name using yahooquery.

    Args:
        company_name (str): The full name of the company (e.g., 'Apple Inc.').

    Returns:
        list[str] or None: List of ticker symbols if found, otherwise None.

    Example:
        >>> get_ticker_symbols_from_name("Apple Inc.")
        ['AAPL', 'APC.F', ...]
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
def get_ticker_symbol_name_from_isin(isin: str) -> str | None:
    """
    Fetch the ticker symbol for a given ISIN using yahooquery.

    Args:
        isin (str): The ISIN (e.g., 'US0378331005' for Apple Inc.).

    Returns:
        str or None: The ticker symbol if found, otherwise None.

    Example:
        >>> get_ticker_symbol_name_from_isin("US0378331005")
        'AAPL'
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
    """
    Example calls for demonstration and manual testing.
    """
    print("get_currency_to_eur_rate():", get_currency_to_eur_rate())
    print("get_ticker_symbols_from_name('Apple Inc.'):", get_ticker_symbols_from_name("Apple Inc."))
    print("get_ticker_symbol_name_from_isin('US0378331005'):", get_ticker_symbol_name_from_isin("US0378331005"))
    print("get_stock_price('AAPL'):", get_stock_price("AAPL"))
