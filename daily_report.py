from fontTools.misc.cython import returns
from openai import OpenAI
from ddgs import DDGS
import feedparser
import requests
import logging
import datetime

import stockdata
import globals

Rss_Feeds_Ticker= [
    "https://www.wallstreet-online.de/rss/nachrichten-aktien-indizes.xml",
    "https://www.finanzen.net/rss/news",
    "https://www.wiwo.de/contentexport/feed/rss/schlagzeilen",
    "https://www.ad-hoc-news.de/rss/nachrichten.xml",
    "https://www.onvista.de/news/feed/rss.xml?orderBy=datetime&newsType%5B0%5D=marketreport&supplier%5B0%5D=dpa-AFX&tags%5B0%5D=Deutschland&",
    "https://api.boerse-frankfurt.de/v1/feeds/news.rss",
    "https://www.aktiencheck.de/rss/news.rss2",
    "https://www.aktiennews24.de/thema/news/feed/",
    "https://www.wallstreet-online.de/rss/board-dax.xml",
    "https://www.deraktionaer.de/aktionaer-news.rss",
    "https://www.derstandard.at/rss/wirtschaft",
    "https://www.diepresse.com/rss/",
    "https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml",
    "https://www.tagesschau.de/wirtschaft/index~rss2.xml",
    "https://rss.orf.at/news.xml"
    ]

Rss_Feeds_General = [
    "https://www.derstandard.at/rss/wirtschaft",
    "https://rss.orf.at/news.xml",
    "https://www.diepresse.com/rss/",
    "https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml",
    "https://www.wallstreet-online.de/rss/nachrichten-aktien-indizes.xml"
    ]


def get_rss_result(tickers, count_per_ticker=25):
    keywords = []
    for (ticker, name) in tickers:
        if ' ' in name:
            name = name.split(' ')[0].lower()
        else:
            name = name.lower()
        if '.' in ticker:
            ticker_short =ticker.split('.')[0].lower()
        else:
            ticker_short = ticker.lower()
        keywords.append((ticker, ticker_short, name))
    news_dict = {ticker: [] for (ticker, _, _) in keywords}
    for feed_url in Rss_Feeds_Ticker:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        response = requests.get(feed_url, headers=headers)
        feed = feedparser.parse(response.content)
        # print(f"Processing feed: {feed_url} with {len(feed.entries)} entries")
        for entry in feed.entries:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            title_lower = title.lower()
            summary_lower = summary.lower()

            for ticker, ticker_short, name in keywords:
                if ticker_short in title_lower or ticker_short in summary_lower or name in title_lower or name in summary_lower:
                    text = f"<news>: {title} :-> {summary}"
                    if text in news_dict[ticker] or len(news_dict[ticker]) >= count_per_ticker:
                        continue
                    news_dict[ticker].append(f"<news>: {title} :-> {summary}")
                    #print(f"    Found entry: {title}")
                    break
    return news_dict


def get_rss_general_news(count=100):
    news_list = []
    line = 0
    for feed_url in Rss_Feeds_General:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        response = requests.get(feed_url, headers=headers)
        feed = feedparser.parse(response.content)
        for entry in feed.entries:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            line += 1
            text = f"    {line:>3}. {title} :-> {summary}"
            if text in news_list or len(news_list) >= count:
                continue
            news_list.append(text)
            if len(news_list) >= count:
                break
        if len(news_list) >= count:
            break
    return '\n'.join(news_list)


def get_duckduckgo_result(company_name, count=5):
    with DDGS() as ddgs:
        results = ddgs.text(f"{company_name} News", max_results=count)
        if results:
            return [('<news>: '+r.get('title')+' :->'+r.get('body')) for r in results[:count] if 'body' in r]
    return []


def collect_news(tickers):
    stock_news = get_rss_result(tickers)
    for (ticker, company_name) in tickers:
        duck_news = get_duckduckgo_result(company_name)
        if duck_news:
            if ticker in stock_news:
                stock_news[ticker].extend(duck_news)
            else:
                stock_news[ticker] = duck_news
    return stock_news


def stock_analyst_bill(response):
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    cost_per_1M_input_usd = 0.25 # USD per 1M tokens for gpt-5-mini
    cost_per_1M_output_usd = 2.00 # USD per 1M tokens for gpt-5-mini
    cost_input_usd = (input_tokens / 1_000_000) * cost_per_1M_input_usd
    cost_output_usd = (output_tokens / 1_000_000) * cost_per_1M_output_usd
    total_cost_usd = cost_input_usd + cost_output_usd
    return total_cost_usd


def stock_analyst(stock_pile, stock_news):
    # stock_pile is a dictionary with keys as ticker symbols and values as dictionaries with keys 'current_price', 'currency', 'rate'
    # stock_news is a dictionary with keys as ticker symbols and values as dictionaries with keys as news source names and values as lists of news strings

    stocks_and_info = "\n"
    for (ticker, info) in stock_pile.items():
        stocks_and_info += f"        - {ticker}: Current Price: {info['current_price']} {info['currency']}"
        if info['rate'] is not None:
            stocks_and_info += f" (Exchange Rate to EUR: {info['rate']})"
        if info.get('regularMarketChangePercent') is not None:
            stocks_and_info += f", Change Percent 24h: {info['regularMarketChangePercent']:.2f}%"
        if info.get('marketCap') is not None:
            stocks_and_info += f", Market Cap: {info['marketCap']}"
        if info.get('fiftyTwoWeekHigh') is not None:
            stocks_and_info += f", 52W High: {info['fiftyTwoWeekHigh']}"
        if info.get('fiftyTwoWeekLow') is not None:
            stocks_and_info += f", 52W Low: {info['fiftyTwoWeekLow']}"
        stocks_and_info += "\n"

    news_section = "\n"
    for ticker, news_list in stock_news.items():
        news_section += f"    {ticker} News:\n"
        for news in news_list:
            news = news.replace('\n', ' ').replace('\r', ' ')
            news_section += f"        {news}\n"

    prompt = f"""    
    Given the following stock information, 
        provide a table of the stocks the table shall contain 3 columns: Ticker, Chance indicator(0-100), Verbal explanation of the chance indicator.
        provide a table of the stocks the table shall contain 3 columns: Ticker, Risk indicator(0-100), Verbal explanation of the risk indicator.
    The chance and risk indicators should be based on the 
        current price and 
        the sector the company is in,
        recent news about the company,
        upcoming earnings reports,
        competition in the market,
        If the stock is not traded in EUR, consider the exchange rate risk to EUR if there is an additional risk.
    The indicators should be a number between 0 and 100, where 0 means no chance/risk and 100 means very high chance/risk.
    Provide the tables in csv format, the ticker name, as well as the Verbal explanation shall be within quotes ("), the risk number and chance number shall be integer numbers without quotes.
    Only provide the tables, no additional text.
    Make sure the csv format is correct, so that it can be easily imported into a spreadsheet program.
    If you do not have enough information to provide a chance or risk indicator, use 0 for chance and 100 for risk, and explain in the verbal explanation that there was not enough information.
    Do not make up information, only use what is provided and what you can find in a web search.
    The explanations should be concise, no more than 200 words, and in German.
    Use the following format for the tables:
    Chance Table:
    "AAPL",85,"Apple Inc. has strong market position and positive recent news."
    "RHM.DE",60,"Rheinmetall AG is in a volatile sector with mixed recent news."
    Risk Table:
    "AAPL",15,"Apple Inc. has low risk due to its diversified product line."
    "RHM.DE",40,"Rheinmetall AG faces risks from geopolitical tensions affecting its defense contracts."    
    
    Here is the stock information: {stocks_and_info}
    Here is the recent news information: {news_section}
    """
    logging.info('USER PROMPT:'+prompt)
    client = OpenAI(api_key=globals.USER_CONFIG["OPEN_AI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "Du bist ein deutschsprachiger Finanzanalyst. Antworte ausschließlich im CSV-Tabellenformat, ohne zusätzlichen Text, aber ver den Tabellen ist eine Zeile mit der Tabellenüberschrift  'Chance Table:' und 'Risk Table:'."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=10000,
        n=1,
        stop=None,
    )
    logging.info('AI RESPONSE:\n'+"\n    ".join(response.choices[0].message.content.splitlines()).strip())
    # generate a dictionary from the response
    # keys are the ticker symbols
    # values are a dictionary with keys 'chance' and 'risk'
    # each value is a tuple of (number, explanation)
    # e.g. {'AAPL': {'chance': (85, 'Apple Inc. has strong market position and positive recent news.'), 'risk': (15, 'Apple Inc. has low risk due to its diversified product line.')}, ...}
    result_dict = {}
    in_chance_table = False
    in_risk_table = False
    for line in response.choices[0].message.content.splitlines():
        if "Chance Table:" in line:
            in_chance_table = True
            in_risk_table = False
            continue
        elif "Risk Table:" in line:
            in_chance_table = False
            in_risk_table = True
            continue
        elif line.strip() == "":
            continue
        if in_chance_table:
            parts = line.split(',')
            if len(parts) < 3:
                continue
            ticker = parts[0].strip().strip('"')
            try:
                chance = int(parts[1].strip())
            except ValueError:
                chance = 0
            explanation = ','.join(parts[2:]).strip().strip('"')
            if ticker in result_dict:
                result_dict[ticker]['chance'] = (chance, explanation)
            else:
                result_dict[ticker] = {'chance': (chance, explanation), 'risk': (None, None)}
        elif in_risk_table:
            parts = line.split(',')
            if len(parts) < 3:
                continue
            ticker = parts[0].strip().strip('"')
            try:
                risk = int(parts[1].strip())
            except ValueError:
                risk = 100
            explanation = ','.join(parts[2:]).strip().strip('"')
            if ticker in result_dict:
                result_dict[ticker]['risk'] = (risk, explanation)
            else:
                result_dict[ticker] = {'chance': (None, None), 'risk': (risk, explanation)}

    total_cost_usd = stock_analyst_bill(response)
    if total_cost_usd is not None:
        logging.info(f"Cost of this analysis: ${total_cost_usd:.6f}")
    return result_dict


def daily_report(tickers):
    stock_pile = {}
    for (ticker,_) in tickers:
        (current_price, currency, rate, regularMarketChangePercent, marketCap, fiftyTwoWeekHigh, fiftyTwoWeekLow) = stockdata.get_stock_price(ticker, True)
        if current_price is None:
            continue
        stock_pile[ticker] = {'current_price': current_price, 'currency': currency, 'rate': rate, 'regularMarketChangePercent': regularMarketChangePercent, 'marketCap': marketCap, 'fiftyTwoWeekHigh': fiftyTwoWeekHigh, 'fiftyTwoWeekLow': fiftyTwoWeekLow}
    stock_news = collect_news(tickers)

    logging.basicConfig(filename='ai_analysis.log', level=logging.INFO, format='%(asctime)s %(message)s')
    analyst_dict = stock_analyst(stock_pile, stock_news)

    return analyst_dict


def diversification_report(analyst_dict):
    industries = analyst_dict.get('industry', {})
    now = datetime.datetime.now()

    prompt = "Here is a summary of Industries your customer currently has invested:\n\n"
    prompt += "Industries:\n"
    total_industry_value = sum(industries.values())
    for industry, value in industries.items():
        percentage = (value / total_industry_value) * 100 if total_industry_value > 0 else 0
        prompt += f" - {industry}: {value:.2f} EUR ({percentage:.2f}%)\n"
    prompt += f"""
currently we have {now.strftime("%B %Y")}, the customer plans to invest for the next quarter, 
but does not wanna sell anything. Dont claim about this, just offer invests in new industries.
Please provide a diversification analysis of the current industries, and suggest which industries
could be increased for better diversification.
Consider market trends(also saisonal effects), economic outlook, and potential risks associated with each industry.
for stocks not traded in EUR consider the exchange rate risk to EUR. depending on the currency and its volatility.
Provide your analysis in German.
Here are some actual news ticker headlines that might be relevant for the analysis:
{get_rss_general_news(250)}
--------------------------------
Give a formated concise analysis, no more than 300 words. 
Ending with a summary of the top 3 industries to consider for increased investment,
and a brief explanation for each choice.
Each Industry suggestion should be attached 3 suggested Tickernames. The thicker shall be enclosed by [].

Do not ask for or offer follow up tasks, just provide the requested analysis.
"""
    logging.basicConfig(filename='ai_analysis.log', level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('USER  PROMPT:'+prompt)
    client = OpenAI(api_key=globals.USER_CONFIG["OPEN_AI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system",
             "content": "Du bist ein deutschsprachiger Finanzanalyst. Deine Anworten sollen auf 80 Zeichen pro Zeile begrenzt sein."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=10000,
        n=1,
        stop=None,
    )
    logging.info('AI RESPONSE:\n' + "\n    ".join(response.choices[0].message.content.splitlines()).strip())
    total_cost_usd = stock_analyst_bill(response)
    if total_cost_usd is not None:
        logging.info(f"Cost of this analysis: ${total_cost_usd:.6f}")
    return response.choices[0].message.content


if __name__ == "__main__":
    stock = ["AAPL", "RHM.DE"]
    sectors_and_industries = {'sector': {'Industrials': 596.1121725248639, 'Technology': 508.443041514654,
                'Consumer Cyclical': 99.53033988316498, 'Utilities': 254.53397362200002},
     'industry': {'Aerospace & Defense': 500.45248188, 'Consumer Electronics': 508.443041514654,
                  'Restaurants': 99.53033988316498, 'Utilities - Renewable': 104.76266864000002,
                  'Railroads': 95.65969064486399, 'Utilities - Diversified': 149.771304982}}

    #is_mydb = Db.Db()
    #tickers = [(ticker, name) for ticker in stock if (name := is_mydb.get_stockname(ticker)) is not None]
    #print(tickers)
    #print(daily_report(tickers))
    #print(get_rss_result(tickers))
    if False:
        news = collect_news(tickers)
        for (ticker, news_list) in news.items():
            print(f"{ticker} News:")
            for news in news_list:
                print(f"    - {news}")
            print()
    print( diversification_report(sectors_and_industries))
