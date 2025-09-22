import datetime
import logging
from openai import OpenAI

import RSS_Crawler
import globals
import tools


Rss_Feeds_General = [
    "https://www.derstandard.at/rss/wirtschaft",
    "https://rss.orf.at/news.xml",
    "https://www.diepresse.com/rss/",
    "https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml",
    "https://www.wallstreet-online.de/rss/nachrichten-aktien-indizes.xml"
    ]

def open_ai_bill(response):
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    cost_per_1M_input_usd = 0.25  # USD per 1M tokens for gpt-5-mini
    cost_per_1M_output_usd = 2.00  # USD per 1M tokens for gpt-5-mini
    cost_input_usd = (input_tokens / 1_000_000) * cost_per_1M_input_usd
    cost_output_usd = (output_tokens / 1_000_000) * cost_per_1M_output_usd
    total_cost_usd = cost_input_usd + cost_output_usd
    return total_cost_usd


def get_rss_general_news():
    filter_words = ["trade", "inflation", "interest rate", "economy", "recession", "growth", "market", "stocks", "bonds",
                    "commodities", "forex", "crude oil", "gold", "silver","real estate", "housing", "unemployment", "jobs",
                    "manufacturing", "services", "consumer", "spending", "supply chain", "geopolitics", "policy", "federal reserve",
                    "ECB", "central bank", "earnings", "profit", "loss", "dividend", "merger", "acquisition", "IPO", "regulation", "taxes",
                    "Aktien", "Anleihen", "Rohstoffe", "Devisen", "Immobilien", "Arbeitslosigkeit", "Beschäftigung",
                    "Herstellung", "Dienstleistungen", "Verbraucher", "Ausgaben",
                    "Lieferkette", "Geopolitik", "Politik", "Zentralbank", "Gewinn", "Verlust", "Dividende", "Fusion", "Übernahme",
                    "Börsengang", "Regulierung", "Steuern", "Inflation", "Zinssatz", "Wirtschaft", "Rezession", "Wachstum", "Markt",
                    "Handel"]
    news_list = []
    crawler = RSS_Crawler.RssCrawler(Rss_Feeds_General)
    for entry in crawler.filtered_entries(filter_words):
        info = entry.get_artictle_snippet(filter_words, 75, 75) if entry.article else entry.summary
        news_list.append({'title': entry.title, 'info': info})

    news_section = "\n"
    for data in news_list:
        news_section += f"        {data['title']}:\n            "
        news_section += "\n            ".join(
            tools.wrap_text_with_preferred_breaks(data['info'], 80).splitlines()) + '\n'

    return news_section


def get_Report(analyst_dict):
    logging.basicConfig(filename='ai_diversication_report.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')

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
        {get_rss_general_news()}
        --------------------------------
        Give a formated concise analysis, no more than 300 words. 
        Ending with a summary of the top 3 industries to consider for increased investment,
        and a brief explanation for each choice.
        Each Industry suggestion should be attached 3 suggested Tickernames. Each Tickername shall be enclosed by [].

        Do not ask for or offer follow up tasks, just provide the requested analysis.
        """
    logging.basicConfig(filename='ai_analysis.log', level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('USER  PROMPT:' + prompt)

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
    total_cost_usd = open_ai_bill(response)
    if total_cost_usd is not None:
        logging.info(f"Cost of this analysis: ${total_cost_usd:.6f}")
    return response.choices[0].message.content