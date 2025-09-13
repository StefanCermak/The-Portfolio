import tkinter.ttk as ttk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Callable, Any
import re
import webbrowser

import globals
import stockdata
import Db
import threading
import daily_report

class StatisticsTab:
    """
    Tab for displaying and managing portfolio statistics.
    Shows statistics for active trades, trade history, and dividends.
    """
    def __init__(self, parent: Any, register_update_all_tabs: Callable[[Callable[[], None]], None]) -> None:
        """
        Initialize the StatisticsTab with all statistics sections.

        Args:
            parent: The parent tkinter widget.
            register_update_all_tabs: Function to register the update callback.
        """
        self.db = Db.Db()
        register_update_all_tabs(self.update_tab_statistics)

        self.frame_row_1 = ttk.Frame(parent)
        self.frame_row_1.grid(column=0, row=0, padx=0, pady=0, sticky="nsew")
        self.frame_row_2 = ttk.Frame(parent)
        self.frame_row_2.grid(column=0, row=1, padx=0, pady=0, sticky="nsew")
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self.frame_active = ttk.LabelFrame(self.frame_row_1, text="Active Trades Statistics")
        self.frame_active.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")
        self.frame_history = ttk.LabelFrame(self.frame_row_1, text="Trade History Statistics")
        self.frame_history.grid(column=1, row=0, padx=10, pady=10, sticky="nsew")
        self.frame_dividends = ttk.LabelFrame(self.frame_row_1, text="Dividends Statistics")
        self.frame_dividends.grid(column=2, row=0, padx=10, pady=10, sticky="nsew")
        self.frame_pie_chart = ttk.LabelFrame(self.frame_row_2, text="Portfolio Distribution")
        self.frame_pie_chart.grid(column=0, row=0, columnspan=1, padx=10, pady=10, sticky="nsew")
        self.frame_diversivication = ttk.LabelFrame(self.frame_row_2, text="Diversification")
        self.frame_diversivication.grid(column=1, row=0, columnspan=1, padx=10, pady=10, sticky="nsew")

        self.label_active_stocks = ttk.Label(self.frame_active, text=f"Different Stocks: #")
        self.label_active_stocks.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.label_active_invest = ttk.Label(self.frame_active, text=f"Total Invest: # EUR")
        self.label_active_invest.grid(column=0, row=1, padx=10, pady=10, sticky="w")
        self.label_active_current_value = ttk.Label(self.frame_active, text=f"Total Current Value: # EUR")
        self.label_active_current_value.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.label_active_profit = ttk.Label(self.frame_active, text=f"Total Profit: # EUR (# %)")
        self.label_active_profit.grid(column=0, row=3, padx=10, pady=10, sticky="w")

        self.label_history_stocks = ttk.Label(self.frame_history, text=f"Different Stocks: #")
        self.label_history_stocks.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.label_history_invest = ttk.Label(self.frame_history, text=f"Total Invest: # EUR")
        self.label_history_invest.grid(column=0, row=1, padx=10, pady=10, sticky="w")
        self.label_history_exit = ttk.Label(self.frame_history, text=f"Total Exit: # EUR")
        self.label_history_exit.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.label_history_profit = ttk.Label(self.frame_history, text=f"Total Profit: # EUR (# %)")
        self.label_history_profit.grid(column=0, row=3, padx=10, pady=10, sticky="w")
        self.label_history_profit_per_year = ttk.Label(self.frame_history, text=f"Average profit per Year: # EUR (# %)")
        self.label_history_profit_per_year.grid(column=0, row=4, padx=10, pady=10, sticky="w")

        # Dividends statistics - not implemented yet

        # Pie chart for portfolio distribution
        # one subplot for industry, one for sector

        screen_dpi = parent.winfo_fpixels('1i')
        self.fig, self.ax = plt.subplots(1,2, figsize=(5, 2.5), dpi=screen_dpi)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_pie_chart)
        self.canvas.get_tk_widget().grid(column=0, row=0, padx=10, pady=10)

        # diversification -
        self.button_call_ai_plan = ttk.Button(self.frame_diversivication, text="🧠Diversification Plan", command=self.call_ai_for_diversification_plan)
        self.button_call_ai_plan.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.info_diversification = tk.Text(self.frame_diversivication, width=80, height=25, wrap="word")
        self.info_diversification.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
        date, ai_text = self.db.get_diversification_analysis()
        if ai_text is None or ai_text == "":
            ai_text = "No diversification analysis available. Click the button above to generate a diversification plan using AI."
        else:
            ai_text = f"Last analysis from {date}:\n\n{ai_text}"
        self.insert_diversification_text_with_links(ai_text)
        # disable editing
        self.info_diversification.config(state=tk.DISABLED)

        self.update_tab_statistics()

    def insert_diversification_text_with_links(self, text: str) -> None:
        """
        Inserts text into self.info_diversification, making ticker symbols in [TICKER] clickable.
        Clicking a ticker opens its Yahoo Finance page in the browser.
        """
        self.info_diversification.config(state=tk.NORMAL)
        self.info_diversification.delete("1.0", tk.END)
        pattern = re.compile(r'\[([A-Z0-9\.\-]+)\]')
        pos = 0
        for match in pattern.finditer(text):
            start, end = match.span()
            ticker = match.group(1)
            # Insert text before the ticker
            self.info_diversification.insert(tk.END, text[pos:start])
            tag_name = f"ticker_{ticker}_{start}"
            self.info_diversification.insert(tk.END, f"[{ticker}]", tag_name)
            self.info_diversification.tag_config(
                tag_name,
                foreground="blue",
                underline=1,
                font=("TkDefaultFont", 9, "underline")
            )
            def callback(event, ticker=ticker):
                url = f"https://finance.yahoo.com/quote/{ticker}/"
                webbrowser.open(url)
            self.info_diversification.tag_bind(tag_name, "<Button-1>", callback)
            pos = end
        # Insert remaining text
        self.info_diversification.insert(tk.END, text[pos:])
        self.info_diversification.config(state=tk.DISABLED)

    def _get_sectors_and_industries_invest(self, shorten: bool = True) -> dict:
        """
        Helper function to get the total investment per sector and industry.

        Returns:
            dict: A dictionary with sectors and industries as keys and their total investment as values.
        """
        current_stocks = self.db.get_current_stock_set()
        sector_invest_eur = {}
        industry_invest_eur = {}
        for stockname, data_array in current_stocks.items():
            ticker_symbol = self.db.get_ticker_symbol(stockname)
            current_price, currency, rate = stockdata.get_stock_price(ticker_symbol)
            (industry, sector) = stockdata.get_industry_and_sector(ticker_symbol)
            if shorten:
                industry = industry.replace(' - ', '\n').replace(' & ', '\n').replace(' ', '\n') if industry is not None else None
                sector = sector.replace(' - ', '\n').replace(' & ', '\n').replace(' ', '\n') if sector is not None else None
                industry = industry.replace('Restaurants', 'Restos') if industry is not None else None
                industry = industry.replace('Biotechnology', 'BioTech.') if industry is not None else None
                industry = industry.replace('Pharmaceuticals', 'Pharma.') if industry is not None else None
                industry = industry.replace('Semiconductors', 'Semi.') if industry is not None else None
                industry = industry.replace('Software', 'SW') if industry is not None else None
                industry = industry.replace('Technology', 'Tech.') if industry is not None else None
                industry = industry.replace('Consumer', 'Cons.') if industry is not None else None
                sector = sector.replace('Technology', 'Tech.') if sector is not None else None
                sector = sector.replace('Consumer', 'Cons.') if sector is not None else None
                sector = sector.replace('Industrials', 'Indus.') if sector is not None else None
                sector = sector.replace('Healthcare', 'Health.') if sector is not None else None
            for data in data_array:
                if current_price is not None and rate is not None:
                    invest = data['quantity'] * current_price * rate
                elif current_price is not None:
                    invest = data['quantity'] * current_price
                else:
                    invest = 0.0
                if industry is not None:
                    if industry not in industry_invest_eur:
                        industry_invest_eur[industry] = 0.0
                    industry_invest_eur[industry] += invest
                if sector is not None:
                    if sector not in sector_invest_eur:
                        sector_invest_eur[sector] = 0.0
                    sector_invest_eur[sector] += invest
        return {'sector': sector_invest_eur, 'industry': industry_invest_eur}

    def update_tab_statistics(self) -> None:
        """
        Updates the statistics display for active and historical trades.
        Calculates and sets values for number of stocks, total investment,
        current value, profit, and average profit per year.
        """
        # Active Trades Statistics
        current_stocks = self.db.get_current_stock_set()
        stocks = set()
        total_invest = 0.0
        total_current_value = 0.0
        for stockname, data_array in current_stocks.items():
            stocks.add(stockname)
            current_price, currency, rate = stockdata.get_stock_price(self.db.get_ticker_symbol(stockname))
            for data in data_array:
                total_invest += data['invest']
                if current_price is not None and rate is not None:
                    total_current_value += data['quantity'] * current_price * rate
                elif current_price is not None:
                    total_current_value += data['quantity'] * current_price
        total_profit = total_current_value - total_invest
        profit_percent = (total_profit / total_invest * 100) if total_invest != 0 else 0.0
        self.label_active_stocks.config(text=f"Different Stocks: {len(stocks)}")
        self.label_active_invest.config(text=f"Total Invest: {total_invest:.2f} {globals.CURRENCY}")
        self.label_active_current_value.config(text=f"Total Current Value: {total_current_value:.2f} EUR")
        self.label_active_profit.config(
            text=f"Total Profit: {total_profit:.2f} EUR ({profit_percent:.2f} %)")

        # Trade History Statistics
        history_stocks = self.db.get_history_stock_set()
        stocks = set()
        total_invest = 0.0
        total_exit = 0.0
        total_profit = 0.0
        total_days = 0
        for stockname, data_array in history_stocks.items():
            stocks.add(stockname)
            for data in data_array:
                total_invest += data['sum_buy']
                total_exit += data['sum_sell']
                profit = data['sum_sell'] - data['sum_buy']
                total_profit += profit
                total_days += (data['end_date'] - data['start_date']).days
        profit_percent = (total_profit / total_invest * 100) if total_invest != 0 else 0.0
        avg_profit_per_year = ((1 + (total_profit / total_invest)) ** (
                365 / total_days) - 1) * 100 if total_days > 0 else 0.0
        if total_days == 0:
            avg_profit_per_year = 0.0
            total_days = 1  # avoid division by zero
        self.label_history_stocks.config(text=f"Different Stocks: {len(stocks)}")
        self.label_history_invest.config(text=f"Total Invest: {total_invest:.2f} {globals.CURRENCY}")
        self.label_history_exit.config(text=f"Total Exit: {total_exit:.2f} {globals.CURRENCY}")
        self.label_history_profit.config(
            text=f"Total Profit: {total_profit:.2f} {globals.CURRENCY} ({profit_percent:.2f} %)")
        self.label_history_profit_per_year.config(
            text=f"Average profit per Year: {(total_profit / total_days * 365):.2f} {globals.CURRENCY} ({avg_profit_per_year:.2f} %)")
        # Dividends Statistics
        # Not implemented yet

        # Pie Chart
        sectors_and_industries = self._get_sectors_and_industries_invest()
        value_sector_eur = sectors_and_industries['sector']
        value_industry_eur = sectors_and_industries['industry']
        # mixed sorting 1st biggest value, 2nd smallest value, 3th 2nd biggest value, 4th 2nd smallest value, ...
        # so that small values are between big segments
        value_sector_eur = dict(sorted(value_sector_eur.items(), key=lambda item: item[1], reverse=True))
        value_industry_eur = dict(sorted(value_industry_eur.items(), key=lambda item: item[1], reverse=True))
        if len(value_sector_eur) > 4:
            keys = list(value_sector_eur.keys())
            values = list(value_sector_eur.values())
            new_keys = []
            new_values = []
            for i in range((len(keys) + 1) // 2):
                new_keys.append(keys[i])
                new_values.append(values[i])
                if i != len(keys) - i - 1:
                    new_keys.append(keys[len(keys) - i - 1])
                    new_values.append(values[len(keys) - i - 1])
            value_sector_eur = dict(zip(new_keys, new_values))
        if len(value_industry_eur) > 4:
            keys = list(value_industry_eur.keys())
            values = list(value_industry_eur.values())
            new_keys = []
            new_values = []
            for i in range((len(keys) + 1) // 2):
                new_keys.append(keys[i])
                new_values.append(values[i])
                if i != len(keys) - i - 1:
                    new_keys.append(keys[len(keys) - i - 1])
                    new_values.append(values[len(keys) - i - 1])
            value_industry_eur = dict(zip(new_keys, new_values))

        # limit to top 10
        # Plot pie chart
        # industry is subplot (1,1), sector is subplot (1,2)
        self.ax[0].clear()
        self.ax[1].clear()
        if len(value_industry_eur) > 0:
            self.ax[0].pie(
                value_industry_eur.values(),
                labels=value_industry_eur.keys(),
                # autopct='%1.1f%%',
                startangle=140,
                textprops={'fontsize': 6, 'horizontalalignment': 'center'},
                labeldistance=0.8,
                radius=1.4
            )
            self.ax[0].text(0, 0, 'Industry', ha='center', va='center', fontsize=10, fontweight='bold')
        else:
            self.ax[0].text(0.5, 0.5, 'No Data', horizontalalignment='center', verticalalignment='center', fontsize=8)
            self.ax[0].set_title('Industry', fontsize=10)
        if len(value_sector_eur) > 0:
            self.ax[1].pie(
                value_sector_eur.values(),
                labels=value_sector_eur.keys(),
                # autopct='%1.1f%%',
                startangle=140,
                textprops={'fontsize': 6, 'horizontalalignment': 'center'},
                labeldistance=0.8,
                radius=1.4
            )
            self.ax[1].text(0, 0, 'Sector', ha='center', va='center', fontsize=10, fontweight='bold')
        else:
            self.ax[1].text(0.5, 0.5, 'No Data', horizontalalignment='center', verticalalignment='center', fontsize=8)
            self.ax[1].set_title('Sector', fontsize=10)
        self.fig.tight_layout()
        self.canvas.draw()

    def call_ai_for_diversification_plan(self) -> None:
        """
        Calls an AI service to generate a diversification plan based on current portfolio data.
        The result is displayed in the info_diversification text widget.
        """

        def run_diversification_thread(sectors_and_industries):
            try:
                self.button_call_ai_plan.config(state=tk.DISABLED)
                self.button_call_ai_plan.config(text="🧠💭💭💭💭")
                ai_text = daily_report.diversification_report(sectors_and_industries)
                self.info_diversification.after(0, lambda: handle_ai_text(ai_text))
            except Exception as e:
                def _show_error_and_reset():
                    self.info_diversification.config(state=tk.NORMAL)
                    self.info_diversification.delete("1.0", tk.END)
                    self.info_diversification.insert(tk.END, f"AI diversification analysis failed:\n{str(e)}")
                    self.info_diversification.config(state=tk.DISABLED)
                    self.button_call_ai_plan.config(state=tk.NORMAL)
                    self.button_call_ai_plan.config(text="🧠Diversification Plan")
                self.info_diversification.after(0, _show_error_and_reset)

        def handle_ai_text(ai_text):
            self.db.add_diversification_analysis(ai_text)
            self.insert_diversification_text_with_links(ai_text)
            self.button_call_ai_plan.config(state=tk.NORMAL)
            self.button_call_ai_plan.config(text="🧠Diversification Plan")

        sectors_and_industries = self._get_sectors_and_industries_invest(shorten=False)
        threading.Thread(target=run_diversification_thread, args=(sectors_and_industries,), daemon=True).start()
