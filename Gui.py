import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

from tkcalendar import DateEntry

import datetime

import globals
import Db
import stockdata
import tools
import import_account_statements
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

""" GUI for the stock broker application """

class BrokerApp:
    def __init__(self):
        self.db = Db.Db()

        self.Window = tk.Tk()
        self.Window.title(globals.APP_NAME)
        self.tab_control = ttk.Notebook(self.Window)

        self.active_trades_tab = ttk.Frame(self.tab_control)
        self.trade_history_tab = ttk.Frame(self.tab_control)
        self.add_trade_tab = ttk.Frame(self.tab_control)
        self.sell_tab = ttk.Frame(self.tab_control)
        self.statistics_tab = ttk.Frame(self.tab_control)
        self.settings_tab = ttk.Frame(self.tab_control)
        self.about_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.active_trades_tab, text='Active Trades')
        self.tab_control.add(self.trade_history_tab, text='Trade History')
        self.tab_control.add(self.add_trade_tab, text='Add Trade')
        self.tab_control.add(self.sell_tab, text='Sell Stock')
        self.tab_control.add(self.statistics_tab, text='Statistics')
        self.tab_control.add(self.settings_tab, text='Settings')
        self.tab_control.add(self.about_tab, text='About')
        self.tab_control.pack(expand=1, fill='both')

        self.setup_tab_add_trade()
        self.setup_tab_active_trades()
        self.setup_tab_trade_history()
        self.setup_tab_sell()
        self.setup_tab_statistics()
        self.setup_tab_settings()
        self.setup_tab_about()

    def setup_tab_active_trades(self):
        self.active_trades_tab.columnconfigure(0, weight=1)
        self.active_trades_tab.rowconfigure(0, weight=1)
        self.treeview_active_trades = ttk.Treeview(
            self.active_trades_tab,
            columns=("Stock Name", "Quantity", "Invest", "Now", "Profit"),
            show='tree headings'
        )
        self.treeview_active_trades.heading("Stock Name", text="Stock Name")
        self.treeview_active_trades.heading("Quantity", text="Quantity")
        self.treeview_active_trades.heading("Invest", text="Invest")
        self.treeview_active_trades.heading("Now", text="Now")
        self.treeview_active_trades.heading("Profit", text="Profit")
        self.treeview_active_trades.column("#0", width=30, stretch=False)
        #set Quantity column width to 12 characters, so that the quantity fits in the column, disable stretching
        self.treeview_active_trades.column("Quantity", width=120, stretch=False)
        #set Invest column width to 15 characters, so that the amount fits in the column, disable stretching
        self.treeview_active_trades.column("Invest", width=150, stretch=False)
        #set Now column width to 32 characters, so that the amount fits in the column, disable stretching
        self.treeview_active_trades.column("Now", width=200, stretch=False)
        #set Profit column width to 20 characters, so that the amount fits in the column, disable stretching
        self.treeview_active_trades.column("Profit", width=200, stretch=False)

        self.treeview_active_trades.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")
        self.treeview_active_trades.tag_configure('profit_positive', foreground='green')
        self.treeview_active_trades.tag_configure('profit_negative', foreground='red')
        self.treeview_active_trades.tag_configure('neutral', foreground='blue')

        self.update_tab_active_trades()

    def setup_tab_trade_history(self):
        self.trade_history_tab.columnconfigure(0, weight=1)
        self.trade_history_tab.rowconfigure(0, weight=1)
        self.treeview_trade_history = ttk.Treeview(
            self.trade_history_tab,
            columns=("Stock Name", "Start Date", "End Date", "Sum Buy", "Sum Sell", "Profit", "Profit %", "Profit %(Year"),
            show='tree headings'
        )
        self.treeview_trade_history.heading("Stock Name", text="Stock Name")
        self.treeview_trade_history.heading("Start Date", text="Start Date")
        self.treeview_trade_history.heading("End Date", text="End Date")
        self.treeview_trade_history.heading("Sum Buy", text="Sum Buy")
        self.treeview_trade_history.heading("Sum Sell", text="Sum Sell")
        self.treeview_trade_history.heading("Profit", text="Profit")
        self.treeview_trade_history.heading("Profit %", text="Profit %")
        self.treeview_trade_history.heading("Profit %(Year", text="Profit %(Year)")
        self.treeview_trade_history.column("#0", width=30, stretch=False)
        #set Start Date and End Date column width to 12 characters, so that the date fits in the column, disable stretching
        self.treeview_trade_history.column("Start Date", width=100, stretch=False)
        self.treeview_trade_history.column("End Date", width=100, stretch=False)
        #set Sum Buy and Sum Sell column width to 15 characters, so that the amount fits in the column, disable stretching
        self.treeview_trade_history.column("Sum Buy", width=120, stretch=False)
        self.treeview_trade_history.column("Sum Sell", width=120, stretch=False)
        self.treeview_trade_history.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")
        self.treeview_trade_history.tag_configure('profit_positive', foreground='green')
        self.treeview_trade_history.tag_configure('profit_negative', foreground='red')
        self.treeview_trade_history.tag_configure('neutral', foreground='blue')

        self.update_tab_trade_history()

    def setup_tab_add_trade(self):
        self.add_label_stockname = ttk.Label(self.add_trade_tab, text="Stock Name:")
        self.add_label_stockname.grid(column=0, row=0, padx=10, pady=10)
        self.add_combobox_stockname = ttk.Combobox(self.add_trade_tab, values=sorted(self.db.get_stock_set()))
        self.add_combobox_stockname.grid(column=1, row=0, padx=10, pady=10)
        self.add_label_ticker = ttk.Label(self.add_trade_tab, text="Ticker:")
        self.add_label_ticker.grid(column=4, row=0, padx=10, pady=10)
        self.add_combobox_ticker = ttk.Combobox(self.add_trade_tab, values=[])
        self.add_combobox_ticker.grid(column=5, row=0, padx=10, pady=10)
        self.add_label_quantity = ttk.Label(self.add_trade_tab, text="Quantity:")
        self.add_label_quantity.grid(column=0, row=1, padx=10, pady=10)
        self.add_entry_quantity = ttk.Entry(self.add_trade_tab)
        self.add_entry_quantity.grid(column=1, row=1, padx=10, pady=10)
        self.add_invest_price = ttk.Label(self.add_trade_tab, text="Invest:")
        self.add_invest_price.grid(column=0, row=2, padx=10, pady=10)
        self.add_entry_invest = ttk.Entry(self.add_trade_tab)
        self.add_entry_invest.grid(column=1, row=2, padx=10, pady=10)
        self.add_label_date = ttk.Label(self.add_trade_tab, text="Trade Date:")
        self.add_label_date.grid(column=0, row=3, padx=10, pady=10)
        self.add_entry_date = DateEntry(self.add_trade_tab, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy',
                                        year=datetime.date.today().year, date=datetime.date.today())
        self.add_entry_date.grid(column=1, row=3, padx=10, pady=10)
        self.button_add_trade = ttk.Button(self.add_trade_tab, text="Add Trade", command=self.add_trade)
        self.button_add_trade.grid(column=0, row=4, columnspan=2, padx=10, pady=10)

        self.add_combobox_stockname.bind("<<ComboboxSelected>>", self.on_add_combobox_stockname_selected)
        self.add_combobox_stockname.bind("<FocusOut>", self.on_add_combobox_stockname_selected)

    def setup_tab_sell(self):
        self.sell_label_stockname = ttk.Label(self.sell_tab, text="Stock Name:")
        self.sell_label_stockname.grid(column=0, row=0, padx=10, pady=10)
        self.sell_combobox_stockname = ttk.Combobox(self.sell_tab, values=sorted(self.db.get_stock_set()), state="readonly")
        self.sell_combobox_stockname.grid(column=1, row=0, padx=10, pady=10)
        self.sell_label_earnings = ttk.Label(self.sell_tab, text="Earnings:")
        self.sell_label_earnings.grid(column=0, row=1, padx=10, pady=10)
        self.sell_entry_earnings = ttk.Entry(self.sell_tab)
        self.sell_entry_earnings.grid(column=1, row=1, padx=10, pady=10)
        self.sell_label_date = ttk.Label(self.sell_tab, text="Sell Date:")
        self.sell_label_date.grid(column=0, row=2, padx=10, pady=10)
        self.sell_entry_date = DateEntry(self.sell_tab, width=12, background='darkblue',
                                         foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy',
                                         year=datetime.date.today().year, date=datetime.date.today())
        self.sell_entry_date.grid(column=1, row=2, padx=10, pady=10)
        self.button_sell = ttk.Button(self.sell_tab, text="Sell Stock", command=self.sell_trade)
        self.button_sell.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

    def setup_tab_statistics(self):
        self.setup_tab_statistics_frame_active = ttk.LabelFrame(self.statistics_tab, text="Active Trades Statistics")
        self.setup_tab_statistics_frame_active.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")
        self.setup_tab_statistics_frame_history = ttk.LabelFrame(self.statistics_tab, text="Trade History Statistics")
        self.setup_tab_statistics_frame_history.grid(column=1, row=0, padx=10, pady=10, sticky="nsew")
        self.setup_tab_statistics_frame_dividends = ttk.LabelFrame(self.statistics_tab, text="Dividends Statistics")
        self.setup_tab_statistics_frame_dividends.grid(column=2, row=0, padx=10, pady=10, sticky="nsew")

        self.label_statistics_active_stocks = ttk.Label(self.setup_tab_statistics_frame_active,
                                                        text=f"Different Stocks: #")
        self.label_statistics_active_stocks.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.label_statistics_active_invest = ttk.Label(self.setup_tab_statistics_frame_active,
                                                        text=f"Total Invest: # EUR")
        self.label_statistics_active_invest.grid(column=0, row=1, padx=10, pady=10, sticky="w")
        self.label_statistics_active_current_value = ttk.Label(self.setup_tab_statistics_frame_active,
                                                        text=f"Total Current Value: # EUR")
        self.label_statistics_active_current_value.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.label_statistics_active_profit = ttk.Label(self.setup_tab_statistics_frame_active,
                                                        text=f"Total Profit: # EUR (# %)")
        self.label_statistics_active_profit.grid(column=0, row=3, padx=10, pady=10, sticky="w")

        self.label_statistics_history_stocks = ttk.Label(self.setup_tab_statistics_frame_history,
                                                        text=f"Different Stocks: #")
        self.label_statistics_history_stocks.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.label_statistics_history_invest = ttk.Label(self.setup_tab_statistics_frame_history,
                                                        text=f"Total Invest: # EUR")
        self.label_statistics_history_invest.grid(column=0, row=1, padx=10, pady=10, sticky="w")
        self.label_statistics_history_exit = ttk.Label(self.setup_tab_statistics_frame_history,
                                                        text=f"Total Exit: # EUR")
        self.label_statistics_history_exit.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.label_statistics_history_profit = ttk.Label(self.setup_tab_statistics_frame_history,
                                                        text=f"Total Profit: # EUR (# %)")
        self.label_statistics_history_profit.grid(column=0, row=3, padx=10, pady=10, sticky="w")
        self.label_statistics_history_profit_per_year = ttk.Label(self.setup_tab_statistics_frame_history,
                                                        text=f"Average profit per Year: # EUR (# %)")
        self.label_statistics_history_profit_per_year.grid(column=0, row=4, padx=10, pady=10, sticky="w")

        self.update_tab_statistics()

    def setup_tab_settings(self):
        self.frame_ticker_matching = ttk.LabelFrame(self.settings_tab, text="Ticker Symbol <-> Personal Stock Name Matching")
        self.frame_ticker_matching.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")
        self.label_ticker_matching = ttk.Label(self.frame_ticker_matching,
                                               text="Select the Stock Name to be shown instead of the Ticker Symbol")
        self.label_ticker_matching.grid(column=0, row=0, padx=10, pady=10, columnspan=4)

        self.setup_combobox_stockname_symbol_matching = ttk.Combobox(self.frame_ticker_matching,
                                                                   values=[], state="readonly")
        self.setup_combobox_stockname_symbol_matching.grid(column=0, row=1, padx=10, pady=10)

        self.setup_combobox_stockname_ticker_matching = ttk.Combobox(self.frame_ticker_matching,
                                                                     values=[],
                                                                     state="readonly")
        self.setup_combobox_stockname_ticker_matching.grid(column=1, row=1, padx=10, pady=10)

        self.setup_edit_stockname_new_symbol = ttk.Entry(self.frame_ticker_matching, width=20)
        self.setup_edit_stockname_new_symbol.grid(column=2, row=1, padx=10, pady=10)


        self.button_store_long_name = ttk.Button(self.frame_ticker_matching, text="Store Long Name", command=self.store_long_name)
        self.button_store_long_name.grid(column=3, row=1, padx=10, pady=10)

        self.setup_combobox_stockname_ticker_matching.bind("<<ComboboxSelected>>", self.on_setup_combobox_stockname_ticker_matching_selected)
        self.setup_combobox_stockname_symbol_matching.bind("<<ComboboxSelected>>", self.on_setup_combobox_stockname_symbol_matching_selected)

        self.frame_import_account_statements = ttk.LabelFrame(self.settings_tab, text="Import Account Statements")
        self.frame_import_account_statements.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
        self.label_import_account_statements_folder = ttk.Label(self.frame_import_account_statements,
                                                                text="Import account statements from PDF files in a folder:")
        self.label_import_account_statements_folder.grid(column=0, row=0, padx=10, pady=10)
        self.strvar_import_account_statements_folder_path = tk.StringVar()
        self.entry_import_account_statements_folder_path = ttk.Entry(self.frame_import_account_statements,
                                                                    textvariable=self.strvar_import_account_statements_folder_path, width=50)
        self.entry_import_account_statements_folder_path.grid(column=1, row=0, padx=10, pady=10)
        self.button_browse_import_account_statements_folder = ttk.Button(self.frame_import_account_statements,
                                                                 text="Browse", command=self.browse_import_account_statements_folder)
        self.button_browse_import_account_statements_folder.grid(column=2, row=0, padx=10, pady=10)
        self.button_import_account_statements = ttk.Button(self.frame_import_account_statements,
                                                          text="Import Account Statements", command=self.import_account_statements)
        self.button_import_account_statements.grid(column=0, row=1, columnspan=3, padx=10, pady=10)
        if "account_statements_folder" in globals.USER_CONFIG and globals.USER_CONFIG["account_statements_folder"] != "":
            self.strvar_import_account_statements_folder_path.set(globals.USER_CONFIG["account_statements_folder"])

        self.update_tab_settings()

    def setup_tab_about(self):
        self.about_label = ttk.Label(self.about_tab,
                                     text=f"{globals.APP_NAME}\nVersion: {globals.APP_VERSION}\nAuthor: {globals.APP_AUTHOR}\n{globals.APP_COPYRIGHT}",
                                     justify="center")
        self.about_label.pack(expand=True)

    def update_all_tabs(self):
        self.update_tab_active_trades()
        self.update_tab_trade_history()
        self.update_tab_add_trade()
        self.update_tab_sell()
        self.update_tab_settings()

    def update_tab_active_trades(self):
        trades = self.db.get_current_stock_set()
        for item in self.treeview_active_trades.get_children():
            self.treeview_active_trades.delete(item)
        portfolio_stock_names = sorted(trades.keys())
        stock_summary = {stockname: { 'id': '', 'quantity': 0, 'invest':0 } for stockname in portfolio_stock_names}
        for trade, data_array in trades.items():
            for data in data_array:
                stock_summary[trade]['quantity'] += data['quantity']
                stock_summary[trade]['invest'] += data['invest']
        for stockname in portfolio_stock_names:
            current_price, currency, rate = stockdata.get_stock_price(self.db.get_ticker_symbol(stockname))
            if current_price is not None and rate is not None:
                euro = stock_summary[stockname]['quantity'] * current_price * rate
                current_value = f"{euro:.2f} EUR ({stock_summary[stockname]['quantity'] * current_price:.2f} {currency})"
                earnings_eur = (euro - stock_summary[stockname]['invest'])
                profit_text = f"{earnings_eur:.2f} EUR ({earnings_eur / stock_summary[stockname]['invest'] * 100:.2f} %)"
            elif current_price is not None:
                euro = stock_summary[stockname]['quantity'] * current_price
                current_value = f"{euro:.2f} {currency}"
                earnings_eur = (euro - stock_summary[stockname]['invest'])
                profit_text = f"{earnings_eur:.2f} {currency} ({earnings_eur / stock_summary[stockname]['invest'] * 100:.2f} %)"
            else:
                current_value = ""
                earnings_eur = None
                profit_text = ""

            tag = 'neutral'
            if earnings_eur is not None:
                if earnings_eur > 0.01:
                    tag = 'profit_positive'
                elif earnings_eur < 0.01:
                    tag = 'profit_negative'

            stock_summary[stockname]['id'] = self.treeview_active_trades.insert('',
                                                                                tk.END,
                                                                                values=(stockname,
                                                                                        f"{stock_summary[stockname]['quantity']:.4f}",
                                                                                        f"{stock_summary[stockname]['invest']:.2f} {globals.CURRENCY}",
                                                                                        current_value,
                                                                                        profit_text
                                                                                        )
                                                                                )
            self.treeview_active_trades.item(stock_summary[stockname]['id'], tags=(tag,))

        for trade, data_array in trades.items():
            sorted_data_array = sorted(data_array, key=lambda d: d['date'], reverse=True)
            current_stock_price, currency, rate = stockdata.get_stock_price(self.db.get_ticker_symbol(trade))
            for data in sorted_data_array:
                if current_stock_price is not None and rate is not None:
                    current_price = data['quantity'] * current_stock_price * rate
                    current_value = f"{current_price:.2f} EUR ({data['quantity'] * current_stock_price:.2f} {currency})"
                    earnings_eur = (current_price - data['invest'])
                elif current_stock_price is not None:
                    current_price = data['quantity'] * current_stock_price
                    current_value = f"{current_price:.2f} {currency}"
                    earnings_eur = (current_price - data['invest'])
                else:
                    current_value = ""
                    earnings_eur = None

                tag = 'neutral'
                if earnings_eur is not None:
                    if earnings_eur > 0.01:
                        tag = 'profit_positive'
                    elif earnings_eur < -0.01:
                        tag = 'profit_negative'

                id = self.treeview_active_trades.insert(stock_summary[trade]['id'],
                                                   tk.END,
                                                   values=('📅'+data['date'].strftime(globals.DATE_FORMAT),
                                                           f"{data['quantity']:.4f}",
                                                           f"{data['invest']:.2f} {globals.CURRENCY}",
                                                           current_value
                                                           )
                                                )
                self.treeview_active_trades.item(id, tags=(tag,))

    def update_tab_trade_history(self):
        trades = self.db.get_history_stock_set()
        for item in self.treeview_trade_history.get_children():
            self.treeview_trade_history.delete(item)
        portfolio_stock_names = sorted(trades.keys())
        for stockname in portfolio_stock_names:
            stock_id = self.treeview_trade_history.insert('',
                                                          tk.END,
                                                          values=(stockname, '', '', '', '')
                                                          )
            data_array = trades[stockname]
            sorted_data_array = sorted(data_array, key=lambda d: d['end_date'], reverse=True)
            sum_profit = 0.0
            for data in sorted_data_array:
                profit_eur = data['sum_sell'] - data['sum_buy']
                profit_percent = (profit_eur / data['sum_buy'] * 100) if data['sum_buy'] != 0 else 0.0
                days_held = (data['end_date'] - data['start_date']).days
                # tages prozensatz = (1 + gesamtprozentsatz)^(1/anzahltage) - 1
                profit_percent_per_day = ( (1 + profit_percent / 100) ** (1/days_held) - 1 ) * 100 if days_held > 0 else 0.0
                # Jahres prozensatz = (1 + tagesprozentsatz)^365 - 1
                profit_percent_per_year = ( (1 + profit_percent_per_day / 100) ** 365 - 1 ) * 100 if days_held > 0 else 0.0
                tag = 'neutral'
                if profit_eur > 0.01:
                    tag = 'profit_positive'
                elif profit_eur < -0.01:
                    tag = 'profit_negative'
                line = self.treeview_trade_history.insert(stock_id,
                                                  tk.END,
                                                  values=(
                                                      '',
                                                      data['start_date'].strftime(globals.DATE_FORMAT),
                                                      data['end_date'].strftime(globals.DATE_FORMAT),
                                                      f"{data['sum_buy']:.2f} {globals.CURRENCY}",
                                                      f"{data['sum_sell']:.2f} {globals.CURRENCY}",
                                                      f"{profit_eur:.2f} {globals.CURRENCY}",
                                                      f"{profit_percent:.2f} %",
                                                      f"{profit_percent_per_year:.2f} %"
                                                  )
                                                  )
                self.treeview_trade_history.item(line, tags=(tag,))
                sum_profit += profit_eur
            tag = 'neutral'
            if sum_profit > 0.01:
                tag = 'profit_positive'
            elif sum_profit < -0.01:
                tag = 'profit_negative'
            self.treeview_trade_history.item(stock_id, tags=(tag,))

    def update_tab_add_trade(self):
        stocknames = sorted(self.db.get_stock_set())
        self.add_combobox_stockname['values'] = stocknames

    def update_tab_settings(self):
        stocknames_with_tickers = self.db.get_stocknames_with_tickers()
        self.setup_combobox_stockname_symbol_matching['values'] = sorted(stocknames_with_tickers.values())
        self.setup_combobox_stockname_ticker_matching['values'] = sorted(stocknames_with_tickers.keys())

    def update_tab_sell(self):
        stocknames = sorted(self.db.get_stock_set())
        self.sell_combobox_stockname['values'] = stocknames

    def update_tab_statistics(self):
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
        self.label_statistics_active_stocks.config(text=f"Different Stocks: {len(stocks)}")
        self.label_statistics_active_invest.config(text=f"Total Invest: {total_invest:.2f} {globals.CURRENCY}")
        self.label_statistics_active_current_value.config(text=f"Total Current Value: {total_current_value:.2f} EUR")
        self.label_statistics_active_profit.config(text=f"Total Profit: {total_profit:.2f} EUR ({profit_percent:.2f} %)")
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
        avg_profit_per_year = ( (1 + (total_profit / total_invest) ) ** (365/total_days) - 1 ) * 100 if total_days > 0 else 0.0
        self.label_statistics_history_stocks.config(text=f"Different Stocks: {len(stocks)}")
        self.label_statistics_history_invest.config(text=f"Total Invest: {total_invest:.2f} {globals.CURRENCY}")
        self.label_statistics_history_exit.config(text=f"Total Exit: {total_exit:.2f} {globals.CURRENCY}")
        self.label_statistics_history_profit.config(text=f"Total Profit: {total_profit:.2f} {globals.CURRENCY} ({profit_percent:.2f} %)")
        self.label_statistics_history_profit_per_year.config(text=f"Average profit per Year: { (total_profit / total_days * 365):.2f} {globals.CURRENCY} ({avg_profit_per_year:.2f} %)")
        # Dividends Statistics
        # Not implemented yet

    def add_trade(self):
        stockname = self.add_combobox_stockname.get()
        ticker_symbol = self.add_combobox_ticker.get()
        quantity = float(self.add_entry_quantity.get().replace(',', '.'))
        price = float(self.add_entry_invest.get().replace(',', '.'))
        trade_date = self.add_entry_date.get_date()

        self.db.add_stockname_ticker(stockname, ticker_symbol)
        self.db.add_stock_trade(ticker_symbol, quantity, price, trade_date)

        self.add_combobox_stockname.set('')
        self.add_entry_quantity.delete(0, tk.END)
        self.add_entry_invest.delete(0, tk.END)
        self.add_entry_date.set_date(datetime.date.today())

        self.update_all_tabs()

    def sell_trade(self):
        stockname = self.sell_combobox_stockname.get()
        earnings = float(self.sell_entry_earnings.get().replace(',', '.'))
        sell_date = self.sell_entry_date.get_date()

        self.db.sell_stock(stockname, earnings, sell_date)

        self.sell_combobox_stockname.set('')
        self.sell_entry_earnings.delete(0, tk.END)
        self.sell_entry_date.set_date(datetime.date.today())

        self.update_all_tabs()

    def store_long_name(self):
        ticker_symbol = self.setup_combobox_stockname_ticker_matching.get()
        stockname = self.setup_edit_stockname_new_symbol.get()
        if ticker_symbol == "" or stockname == "":
            return
        self.db.add_stockname_ticker(stockname, ticker_symbol, True)
        self.update_all_tabs()
        self.setup_combobox_stockname_symbol_matching.set(stockname)


    def browse_import_account_statements_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.strvar_import_account_statements_folder_path.get())
        if folder_path:
            folder_path = tools.path_smart_shorten(folder_path)
            self.strvar_import_account_statements_folder_path.set(folder_path)
            globals.USER_CONFIG["account_statements_folder"] = folder_path
            globals.save_user_config()

    def import_account_statements(self):
        folder_path = self.strvar_import_account_statements_folder_path.get()
        if folder_path:
            import_account_statements.from_folder(folder_path, self.db)
            self.update_all_tabs()

    def on_add_combobox_stockname_selected(self, event):
        stockname = self.add_combobox_stockname.get()
        ticker_symbols = stockdata.get_ticker_symbols_from_name(stockname)
        if ticker_symbols is None:
            self.add_combobox_ticker['values'] = []
            self.add_combobox_ticker.set('')
        else:
            self.add_combobox_ticker['values'] = ticker_symbols
            if len(ticker_symbols) > 0:
                used_symbol = self.db.get_ticker_symbol(stockname)
                if used_symbol in ticker_symbols:
                    self.add_combobox_ticker.set(used_symbol)
                else:
                    self.add_combobox_ticker.set(ticker_symbols[0])

    def on_setup_combobox_stockname_ticker_matching_selected(self, event):
        ticker_symbol = self.setup_combobox_stockname_ticker_matching.get()
        stockname = self.db.get_stockname(ticker_symbol)
        if stockname is not None:
            self.setup_combobox_stockname_symbol_matching.set(stockname)
            self.setup_edit_stockname_new_symbol.delete(0, tk.END)
            self.setup_edit_stockname_new_symbol.insert(0, stockname)

    def on_setup_combobox_stockname_symbol_matching_selected(self, event):
        stockname = self.setup_combobox_stockname_symbol_matching.get()
        ticker_symbol = self.db.get_ticker_symbol(stockname)
        if ticker_symbol is not None:
            self.setup_combobox_stockname_ticker_matching.set(ticker_symbol)
            self.setup_edit_stockname_new_symbol.delete(0, tk.END)
            self.setup_edit_stockname_new_symbol.insert(0, stockname)

    def run(self):
        self.Window.mainloop()
        globals.save_user_config()
