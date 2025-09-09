from openai import OpenAI
from ddgs import DDGS


import stockdata
import globals
import Db

mydb = Db.Db()

def get_duckduckgo_result(ticker, count=10):
    company_name = mydb.get_stockname(ticker)
    with DDGS() as ddgs:
        results = ddgs.text(f"{company_name} News", max_results=count)
        if results:
            return [('<news>: '+r.get('title')+' :->'+r.get('body')) for r in results[:count] if 'body' in r]
    return []

def stock_analyst_bill(response):
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    cost_per_1M_input_usd = 1.25 # USD per 1M tokens for gpt-4
    cost_per_1M_output_usd = 10.00 # USD per 1M tokens for gpt-4
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
        stocks_and_info += "\n"

    news_section = "\n"
    for ticker, sources in stock_news.items():
        news_section += f"{ticker} News:\n"
        for source, news_list in sources.items():
            for news in news_list:
                news_section += f"    - {source}: {news}\n"

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
    The explanations should be concise, no more than 240 words, and in German.
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
    client = OpenAI(api_key=globals.USER_CONFIG["OPEN_AI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )
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
        print(f"Cost of this analysis: ${total_cost_usd:.6f}")
    return result_dict

def daily_report(tickers):
    stock_pile = {}
    stock_news = {}
    for ticker in tickers:
        (current_price, currency, rate) = stockdata.get_stock_price(ticker)
        if current_price is None:
            continue
        stock_pile[ticker] = {'current_price': current_price, 'currency': currency, 'rate': rate}
        stock_news[ticker] = {'DuckDuck': get_duckduckgo_result(ticker)}

    analyst_dict = stock_analyst(stock_pile, stock_news)

    return analyst_dict

if __name__ == "__main__":
    tickers = ["AAPL", "RHM.DE"]

    print(daily_report(tickers))
