import logging

import sektor_report
import globals

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

def open_ai_bill(response):
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    cost_per_1M_input_usd = 0.25  # USD per 1M tokens for gpt-5-mini
    cost_per_1M_output_usd = 2.00  # USD per 1M tokens for gpt-5-mini
    cost_input_usd = (input_tokens / 1_000_000) * cost_per_1M_input_usd
    cost_output_usd = (output_tokens / 1_000_000) * cost_per_1M_output_usd
    total_cost_usd = cost_input_usd + cost_output_usd
    return total_cost_usd

def get_Health_Report(ticker, news):
    logging.basicConfig(filename='ai_health_check.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')
    sektor_report_data = sektor_report.sektor_report([ticker])

    openai = globals.get_openai_client()
    prompt = f"""
    You are a financial expert. Based on the following stock information and sector report, provide a
    concise analysis of the stock's health and potential risks. Highlight any significant news or trends
    that could impact the stock's performance.
    Stock Information:
    {news}
    Sector Report:
    {sektor_report_data}
    Provide your analysis in a clear and structured manner.
    """
    logging.info("Prompt for AI risk and chance analysis:\n" + prompt)
    try:
        response = openai.chat.completions.create(
            model=globals.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a german speaking financial specialist." },
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=10000,
            n=1,
            stop=None,
        )
        analysis = response.choices[0].message.content
        logging.info('AI RAW RESPONSE:\n' + "\n    ".join(analysis.splitlines()).strip())
        total_cost_usd = open_ai_bill(response)
        logging.info('AI RESPONSE COST: $' + f"{total_cost_usd:.6f}")

        return analysis
    except Exception as e:
        logging.error(f"Error generating report for {ticker}: {e}")
        return "Error generating report."
