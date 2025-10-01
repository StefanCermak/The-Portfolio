from tools import timed_cache, persistent_cache, persistent_timed_cache

import yfinance as yf
import yahooquery
from datetime import datetime, timedelta
import pandas as pd

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

@persistent_cache("get_industry_and_sector.json")
def get_industry_and_sector(ticker_symbol: str) -> tuple[str | None, str | None]:
    """
    Fetch the industry and sector for a given ticker symbol using yfinance.

    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).

    Returns:
        tuple: (industry, sector)
            industry (str or None): The industry of the company.
            sector (str or None): The sector of the company.

    Example:
        >>> get_industry_and_sector("AAPL")
        ('Consumer Electronics', 'Technology')
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        stock_info = ticker.info
        #print(stock_info)
        industry = stock_info.get('industry', None)
        sector = stock_info.get('sector', None)
        return industry, sector
    except Exception as _:
        return None, None

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


@timed_cache(ttl_seconds=300)  # 5 minutes cache for day data
def get_stock_day_data(ticker_symbol: str) -> dict | None:
    """
    Fetch the current day's stock data for the given ticker symbol using yfinance.

    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).

    Returns:
        dict: Dictionary with current day's stock information or None on error.
            Contains keys: open, high, low, close, volume, change_percent, dividend_yield, currency,
                          last_dividend, next_ex_date, frequency, last_dividends
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        day_data = {
            'open': info.get('regularMarketOpen'),
            'high': info.get('regularMarketDayHigh'),
            'low': info.get('regularMarketDayLow'),
            'close': info.get('regularMarketPrice'),
            'volume': info.get('regularMarketVolume'),
            'change_percent': info.get('regularMarketChangePercent'),
            'dividend_yield': info.get('dividendYield'),
            'currency': info.get('currency')
        }
        div_info = get_dividend_info(ticker_symbol)
        if div_info:
            day_data['last_dividend'] = div_info.get('last_dividend')
            day_data['next_ex_date'] = div_info.get('next_ex_date')
            day_data['frequency'] = div_info.get('frequency')
            day_data['last_dividends'] = div_info.get('last_dividends', [])
        else:
            day_data['last_dividend'] = None
            day_data['next_ex_date'] = None
            day_data['frequency'] = None
            day_data['last_dividends'] = []
        return day_data
    except Exception as e:
        print(f"Error: Could not fetch day data for {ticker_symbol}: {e}")
        return None


@persistent_timed_cache("get_stock_year_data.json", ttl_seconds=72000)  # 20 hours cache for year data
def get_stock_year_data(ticker_symbol: str) -> dict | None:
    """
    Fetch the last year's stock data for the given ticker symbol using yfinance.

    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).

    Returns:
        dict: Dictionary with historical data or None on error.
            Contains keys: dates, prices, volumes
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1y")
        
        if hist.empty:
            return None
            
        # Convert to lists for easy plotting
        year_data = {
            'dates': hist.index.tolist(),
            'prices': hist['Close'].tolist(),
            'volumes': hist['Volume'].tolist(),
            'opens': hist['Open'].tolist(),
            'highs': hist['High'].tolist(),
            'lows': hist['Low'].tolist()
        }
        
        return year_data
    except Exception as e:
        print(f"Error: Could not fetch year data for {ticker_symbol}: {e}")
        return None


@persistent_timed_cache("get_stock_month_data.json", ttl_seconds=3600)  # 1 hour cache for month data
def get_stock_month_data(ticker_symbol: str) -> dict | None:
    """
    Fetch the last month's stock data for the given ticker symbol using yfinance.

    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).

    Returns:
        dict: Dictionary with historical data or None on error.
            Contains keys: dates, prices, volumes
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1mo")
        
        if hist.empty:
            return None
            
        # Convert to lists for easy plotting
        month_data = {
            'dates': hist.index.tolist(),
            'prices': hist['Close'].tolist(),
            'volumes': hist['Volume'].tolist(),
            'opens': hist['Open'].tolist(),
            'highs': hist['High'].tolist(),
            'lows': hist['Low'].tolist()
        }
        
        return month_data
    except Exception as e:
        print(f"Error: Could not fetch month data for {ticker_symbol}: {e}")
        return None


@persistent_timed_cache("get_stock_all_data.json", ttl_seconds=72000)  # 20 hours cache for all data
def get_stock_all_data(ticker_symbol: str) -> dict | None:
    """
    Fetch all available stock data for the given ticker symbol using yfinance.

    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).

    Returns:
        dict: Dictionary with historical data or None on error.
            Contains keys: dates, prices, volumes
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="max")
        
        if hist.empty:
            return None
            
        # Convert to lists for easy plotting
        all_data = {
            'dates': hist.index.tolist(),
            'prices': hist['Close'].tolist(),
            'volumes': hist['Volume'].tolist(),
            'opens': hist['Open'].tolist(),
            'highs': hist['High'].tolist(),
            'lows': hist['Low'].tolist()
        }
        
        return all_data
    except Exception as e:
        print(f"Error: Could not fetch all data for {ticker_symbol}: {e}")
        return None


@timed_cache(ttl_seconds=60)  # 1 minute cache for day data (non-persistent)
def get_stock_day_chart_data(ticker_symbol: str) -> dict | None:
    """
    Fetch the current day's intraday stock data for the given ticker symbol using yfinance.
    This is different from get_stock_day_data which returns summary info.

    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).

    Returns:
        dict: Dictionary with intraday data or None on error.
            Contains keys: dates, prices, volumes
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1d", interval="5m")
        
        if hist.empty:
            return None
            
        # Convert to lists for easy plotting
        day_chart_data = {
            'dates': hist.index.tolist(),
            'prices': hist['Close'].tolist(),
            'volumes': hist['Volume'].tolist(),
            'opens': hist['Open'].tolist(),
            'highs': hist['High'].tolist(),
            'lows': hist['Low'].tolist()
        }
        
        return day_chart_data
    except Exception as e:
        print(f"Error: Could not fetch day chart data for {ticker_symbol}: {e}")
        return None


@persistent_timed_cache("get_dividend_info.json", ttl_seconds=604800)  # 7 Tage Cache
def get_dividend_info(ticker_symbol: str) -> dict | None:
    """
    Liefert Infos zur letzten Dividende, nächstem Ex-Dividenden-Datum, Auszahlungshäufigkeit und die letzten 4 Dividenden.
    Args:
        ticker_symbol (str): Das Tickersymbol (z.B. 'AAPL').
    Returns:
        dict: { 'last_dividend': float|None, 'next_ex_date': str|None, 'frequency': str|None, 'last_dividends': list }
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        divs = ticker.dividends
        if divs is None or divs.empty:
            return {'last_dividend': None, 'next_ex_date': None, 'frequency': None, 'last_dividends': []}
        # Letzte Dividende
        last_dividend = float(divs.iloc[-1]) if not divs.empty else None
        # Auszahlungshäufigkeit berechnen
        if len(divs) >= 2:
            divs_sorted = divs.sort_index(ascending=False)
            dates = divs_sorted.index[:5]
            if len(dates) >= 2:
                intervals = [(dates[i] - dates[i+1]).days for i in range(len(dates)-1)]
                avg_days = sum(intervals) / len(intervals)
                if avg_days < 40: # 30 + 10 Puffer
                    frequency = "Monatlich"
                elif avg_days < 100: # 3 * 30 + 10 Puffer
                    frequency = "Quartalsweise"
                elif avg_days < 190: # 6 * 30 + 10 Puffer
                    frequency = "Halbjährlich"
                else:
                    frequency = "Jährlich"
            else:
                frequency = None
        else:
            frequency = None
        # Nächstes Ex-Dividenden-Datum
        cal = ticker.calendar
        next_ex_date = None
        if isinstance(cal, pd.DataFrame) and 'exDividendDate' in cal.index:
            ex_date_val = cal.loc['exDividendDate'].values[0]
            if pd.notnull(ex_date_val):
                if isinstance(ex_date_val, (pd.Timestamp, datetime)):
                    next_ex_date = ex_date_val.strftime('%Y-%m-%d')
                else:
                    try:
                        next_ex_date = str(pd.to_datetime(ex_date_val).date())
                    except Exception:
                        next_ex_date = str(ex_date_val)
        # Letzte 4 Dividenden (Datum, Betrag, Rendite)
        last_dividends = []
        currency = None
        try:
            currency = ticker.info.get('currency', None)
        except Exception:
            pass
        price = ticker.info.get('regularMarketPrice', None)
        for i, (date, amount) in enumerate(divs.sort_index(ascending=False).iloc[:4].items()):
            # Berechne Dividendenrendite zum aktuellen Kurs (falls möglich)
            percent = None
            if price and amount:
                percent = round(100 * amount / price, 2)
            # Format Datum: "2025-December"
            date_str = f"{date.year}-{date.strftime('%B')}"
            last_dividends.append({
                'index': i+1,
                'date': date_str,
                'amount': float(amount),
                'percent': percent
            })
        return {
            'last_dividend': last_dividend,
            'next_ex_date': next_ex_date,
            'frequency': frequency,
            'last_dividends': last_dividends
        }
    except Exception as e:
        print(f"Error: Could not fetch dividend info for {ticker_symbol}: {e}")
        return {'last_dividend': None, 'next_ex_date': None, 'frequency': None, 'last_dividends': []}


if __name__ == "__main__":
    """
    Example calls for demonstration and manual testing.
    """
    print("get_currency_to_eur_rate():", get_currency_to_eur_rate())
    print("get_ticker_symbols_from_name('Apple Inc.'):", get_ticker_symbols_from_name("Apple Inc."))
    print("get_ticker_symbol_name_from_isin('US0378331005'):", get_ticker_symbol_name_from_isin("US0378331005"))
    print("get_stock_price('AAPL'):", get_stock_price("AAPL"))
