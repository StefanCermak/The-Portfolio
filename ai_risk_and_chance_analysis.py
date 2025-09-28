import logging
from openai import OpenAI


import stockdata
import RSS_Crawler
import WWW_Crawler
import tools
import globals


def get_Report(tickers):
    logging.basicConfig(filename='ai_risk_and_chance_analysis.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')

    stock_pile = {}
    filter_words = []
    news_list = []
    for (ticker, name) in tickers:
        (current_price, currency, rate, regularMarketChangePercent, marketCap, fiftyTwoWeekHigh,
         fiftyTwoWeekLow) = stockdata.get_stock_price(ticker, True)
        if current_price is None:
            continue
        stock_pile[ticker] = {'stockname': name,
                              'current_price': current_price, 'currency': currency, 'rate': rate,
                              'regularMarketChangePercent': regularMarketChangePercent, 'marketCap': marketCap,
                              'fiftyTwoWeekHigh': fiftyTwoWeekHigh, 'fiftyTwoWeekLow': fiftyTwoWeekLow}
        if '.' in ticker:
            ticker = ticker.split('.')[0].lower()
        filter_words.append(ticker)
        if ' ' in name:
            name = name.split(' ')[0].lower()
        filter_words.append(name)

    crawler = RSS_Crawler.RssCrawler()
    for entry in crawler.filtered_entries(filter_words):
        info = entry.get_artictle_snippet(filter_words, 75, 75) if entry.article else entry.summary
        news_list.append({'title': entry.title, 'info': info})
    for (ticker, name) in tickers:
        duckduckgo_result = WWW_Crawler.WWW_Crawler(name, 2, 1)
        for result in duckduckgo_result:
            news_list.append({'title': result[0], 'info': result[1]})

    analyst_dict = _do_risc_anc_chance_analysis(stock_pile, news_list)

    return analyst_dict


def open_ai_bill(response):
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    cost_per_1M_input_usd = 0.25  # USD per 1M tokens for gpt-5-mini
    cost_per_1M_output_usd = 2.00  # USD per 1M tokens for gpt-5-mini
    cost_input_usd = (input_tokens / 1_000_000) * cost_per_1M_input_usd
    cost_output_usd = (output_tokens / 1_000_000) * cost_per_1M_output_usd
    total_cost_usd = cost_input_usd + cost_output_usd
    return total_cost_usd


def _do_risc_anc_chance_analysis(stock_pile, web_info):
    # stock_pile is a dictionary with keys as ticker symbols and values as dictionaries with keys 'current_price', 'currency', 'rate'
    # stock_news is a dictionary with keys as ticker symbols and values as dictionaries with keys as news source names and values as lists of news strings

    stocks_and_info = "\n    Stocks and Current Prices Information's:\n"
    for (ticker, info) in stock_pile.items():
        stocks_and_info += f"        - {ticker} / {info['stockname']}: Current Price: {info['current_price']} {info['currency']}"
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

    news_section = "\n    News and Articles:\n"
    for data in web_info:
        news_section += f"        {data['title']}:\n            "
        news_section += "\n            ".join(tools.wrap_text_with_preferred_breaks(data['info'], 80).splitlines())+'\n'

    prompt = f"""    
    Given on the following stock information, 
        provide a table of the stocks the table shall contain 3 columns: Ticker, Chance indicator(0-100), Verbal explanation of the chance indicator.
        provide a table of the stocks the table shall contain 3 columns: Ticker, Risk indicator(0-100), Verbal explanation of the risk indicator.
    The chance and risk indicators should be based on the 
        current price and 
        the sector the company is in,
        recent news about the company,
        upcoming earnings reports,
        competition in the market,        
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
    --------------------------------------------------------------------------------
{stocks_and_info}
    --------------------------------------------------------------------------------
{news_section}
    """
    logging.info("Prompt for AI risk and chance analysis:\n" + prompt)
    client = OpenAI(api_key=globals.USER_CONFIG["OPEN_AI_API_KEY"])
    response = client.chat.completions.create(
        model=globals.OPENAI_MODEL,
        messages=[
            {"role": "system",
             "content": "Du bist ein deutschsprachiger Finanzanalyst. Antworte ausschließlich im CSV-Tabellenformat, ohne zusätzlichen Text, aber ver den Tabellen ist eine Zeile mit der Tabellenüberschrift  'Chance Table:' und 'Risk Table:'."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=10000,
        n=1,
        stop=None,
    )
    logging.info('AI RAW RESPONSE:\n' + "\n    ".join(response.choices[0].message.content.splitlines()).strip())
    total_cost_usd = open_ai_bill(response)
    logging.info('AI RESPONSE COST: $' + f"{total_cost_usd:.6f}")

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

    return result_dict
