import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog, messagebox
from tkcalendar import DateEntry

import datetime
import webbrowser
import threading

import globals
import Db
import stockdata
import tools
import import_account_statements
import daily_report

# NEU: Importiere AboutTab
from Gui_about_tab import AboutTab
from Gui_settings_tab import SettingsTab

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


class ToolTip:
    def __init__(self, widget):
        """Initialisiert das Tooltip-Objekt für ein Widget."""
        self.widget = widget
        self.tipwindow = None
        self.label = None

    def showtip(self, text, x, y):
        """Zeigt das Tooltip mit dem gegebenen Text an den Koordinaten (x, y) an."""
        if not text:
            return
        if len(text) > 100:
            text = tools.wrap_text_with_preferred_breaks(text, 80)
        if self.tipwindow:
            tw = self.tipwindow
            if self.label:
                self.label.config(text=text)
            tw.wm_geometry(f"+{x}+{y}")
            return

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        self.label = label = tk.Label(tw, text=text, background="#ffffe0", relief="solid", borderwidth=1,
                                      font=("tahoma", 12, "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        """Blendet das Tooltip aus."""
        tw = self.tipwindow
        self.tipwindow = None
        self.label = None
        if tw:
            tw.destroy()


class BrokerApp:
    def __init__(self):
        """Initialisiert die Hauptanwendung und erstellt alle Tabs und Widgets."""
        self.db = Db.Db()
        self.registered_update_functions = []

        self.Window = tk.Tk()
        self.Window.title(globals.APP_NAME)
        self.tab_control = ttk.Notebook(self.Window)

        self.active_trades_tab = ttk.Frame(self.tab_control)
        self.trade_history_tab = ttk.Frame(self.tab_control)
        self.statistics_tab = ttk.Frame(self.tab_control)
        self.manual_trade_tab = ttk.Frame(self.tab_control)
        self.settings_tab = ttk.Frame(self.tab_control)
        self.about_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.active_trades_tab, text='Active Trades')
        self.tab_control.add(self.trade_history_tab, text='Trade History')
        self.tab_control.add(self.statistics_tab, text='Summary')
        self.tab_control.add(self.manual_trade_tab, text='Manual Trade')
        self.tab_control.add(self.settings_tab, text='Configuration')
        self.tab_control.add(self.about_tab, text='About')
        self.tab_control.pack(expand=1, fill='both')

        self.setup_tab_active_trades()
        self.setup_tab_trade_history()
        self.setup_tab_statistics()
        self.setup_tab_manual_trade()

        SettingsTab(self.settings_tab, self.update_all_tabs, self.register_update_all_tabs)
        AboutTab(self.about_tab)

        self.active_trades_tooltip = ToolTip(self.treeview_active_trades)
        
        # Initialize auto-update for active trades (every 5 minutes)
        self.auto_update_job = None
        self.start_auto_update()

    def setup_tab_active_trades(self):
        """Initialisiert und konfiguriert das Tab für aktive Trades."""
        self.active_trades_tab.sort = "name"
        self.active_trades_tab.columnconfigure(0, weight=1)
        self.active_trades_tab.rowconfigure(0, weight=0)  # Menubar
        self.active_trades_tab.rowconfigure(1, weight=1)  # treeview

        self.active_trades_menu_frame = ttk.Frame(self.active_trades_tab)
        self.active_trades_menu_frame.grid(column=0, row=0, padx=0, pady=0, sticky="nsew")
        self.active_trades_button_ai_analysis = ttk.Button(self.active_trades_menu_frame, text="🧠stock analysis",
                                                           command=self.update_ai_analysis)
        self.active_trades_button_ai_analysis.grid(column=0, row=0, padx=0, pady=0)

        self.treeview_active_trades = ttk.Treeview(
            self.active_trades_tab,
            columns=("Stock Name", "Chance", "Risk", "Quantity", "Invest", "Now", "Profit"),
            show='tree headings'
        )
        self.treeview_active_trades.heading("Stock Name", text="Stock Name", command=self.on_stock_name_heading_click)
        self.treeview_active_trades.heading("Chance", text="++", command=self.on_chance_heading_click)
        self.treeview_active_trades.heading("Risk", text="--", command=self.on_risk_heading_click)
        self.treeview_active_trades.heading("Quantity", text="Quantity", command=self.on_quantity_heading_click)
        self.treeview_active_trades.heading("Invest", text="Invest", command=self.on_invest_heading_click)
        self.treeview_active_trades.heading("Now", text="Now", command=self.on_now_heading_click)
        self.treeview_active_trades.heading("Profit", text="Profit", command=self.on_profit_heading_click)
        self.treeview_active_trades.column("#0", width=30, stretch=False)
        # set Quantity column width to 12 characters, so that the quantity fits in the column, disable stretching
        self.treeview_active_trades.column("Quantity", width=120, stretch=False)
        # set risk and chance column width to 3 characters, so that the amount fits in the column, disable stretching
        self.treeview_active_trades.column("Chance", width=30, stretch=False)
        self.treeview_active_trades.column("Risk", width=30, stretch=False)
        # set Invest column width to 15 characters, so that the amount fits in the column, disable stretching
        self.treeview_active_trades.column("Invest", width=150, stretch=False)
        # set Now column width to 32 characters, so that the amount fits in the column, disable stretching
        self.treeview_active_trades.column("Now", width=200, stretch=False)
        # set Profit column width to 20 characters, so that the amount fits in the column, disable stretching
        self.treeview_active_trades.column("Profit", width=200, stretch=False)

        self.treeview_active_trades.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
        self.treeview_active_trades.tag_configure('profit_positive', foreground='green')
        self.treeview_active_trades.tag_configure('profit_negative', foreground='red')
        self.treeview_active_trades.tag_configure('neutral', foreground='blue')
        self.treeview_active_trades.bind("<Double-Button-1>", self.on_active_trades_treeview_click)
        self.treeview_active_trades.bind("<Motion>", self.on_active_trades_motion)
        self.treeview_active_trades.bind("<Leave>", lambda e: self.active_trades_tooltip.hidetip())

        self.update_tab_active_trades()

    def setup_tab_trade_history(self):
        """Initialisiert und konfiguriert das Tab für die Trade-Historie."""
        self.trade_history_tab.columnconfigure(0, weight=1)
        self.trade_history_tab.rowconfigure(0, weight=1)
        self.treeview_trade_history = ttk.Treeview(
            self.trade_history_tab,
            columns=("Stock Name", "Start Date", "End Date", "Sum Buy", "Sum Sell", "Profit", "Profit %",
                     "Profit %(Year"),
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
        # set Start Date and End Date column width to 12 characters, so that the date fits in the column, disable stretching
        self.treeview_trade_history.column("Start Date", width=100, stretch=False)
        self.treeview_trade_history.column("End Date", width=100, stretch=False)
        # set Sum Buy and Sum Sell column width to 15 characters, so that the amount fits in the column, disable stretching
        self.treeview_trade_history.column("Sum Buy", width=120, stretch=False)
        self.treeview_trade_history.column("Sum Sell", width=120, stretch=False)
        self.treeview_trade_history.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")
        self.treeview_trade_history.tag_configure('profit_positive', foreground='green')
        self.treeview_trade_history.tag_configure('profit_negative', foreground='red')
        self.treeview_trade_history.tag_configure('neutral', foreground='blue')

        self.treeview_trade_history.bind("<Double-Button-1>", self.on_history_trades_treeview_click)

        self.update_tab_trade_history()

    def setup_tab_manual_trade(self):
        """Initialisiert und konfiguriert das Tab für manuelle Trades."""
        self.tab_manual_frame_common = ttk.Frame(self.manual_trade_tab)
        self.tab_manual_frame_common.grid(column=0, row=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.manual_trade_label_stockname = ttk.Label(self.tab_manual_frame_common, text="Stock Name:")
        self.manual_trade_label_stockname.grid(column=0, row=0, padx=10, pady=10)
        self.manual_trade_combobox_stockname = ttk.Combobox(self.tab_manual_frame_common,
                                                            values=sorted(self.db.get_stock_set()))
        self.manual_trade_combobox_stockname.grid(column=1, row=0, padx=10, pady=10)
        self.manual_trade_label_ticker = ttk.Label(self.tab_manual_frame_common, text="Ticker:")
        self.manual_trade_label_ticker.grid(column=4, row=0, padx=10, pady=10)
        self.manual_trade_combobox_ticker = ttk.Combobox(self.tab_manual_frame_common, values=[])
        self.manual_trade_combobox_ticker.grid(column=5, row=0, padx=10, pady=10)
        self.manual_trade_entry_date = DateEntry(self.tab_manual_frame_common, width=12, background='darkblue',
                                                 foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy',
                                                 year=datetime.date.today().year, date=datetime.date.today())
        self.manual_trade_entry_date.grid(column=6, row=0, padx=10, pady=10)
        self.tab_manual_frame_buy = ttk.LabelFrame(self.manual_trade_tab, text="Buy Stock")
        self.tab_manual_frame_buy.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
        self.manual_trade_label_quantity_buy = ttk.Label(self.tab_manual_frame_buy, text="Quantity:")
        self.manual_trade_label_quantity_buy.grid(column=0, row=0, padx=10, pady=10)
        self.manual_trade_entry_quantity_buy = ttk.Entry(self.tab_manual_frame_buy)
        self.manual_trade_entry_quantity_buy.grid(column=1, row=0, padx=10, pady=10)
        self.manual_trade_label_invest_buy = ttk.Label(self.tab_manual_frame_buy, text="Invest:")
        self.manual_trade_label_invest_buy.grid(column=0, row=1, padx=10, pady=10)
        self.manual_trade_entry_invest_buy = ttk.Entry(self.tab_manual_frame_buy)
        self.manual_trade_entry_invest_buy.grid(column=1, row=1, padx=10, pady=10)
        self.manual_trade_button_buy = ttk.Button(self.tab_manual_frame_buy, text="Buy Stock", command=self.add_trade)
        self.manual_trade_button_buy.grid(column=0, row=2, columnspan=2, padx=10, pady=10)
        self.tab_manual_frame_sell = ttk.LabelFrame(self.manual_trade_tab, text="Sell Stock")
        self.tab_manual_frame_sell.grid(column=1, row=1, padx=10, pady=10, sticky="nsew")
        self.manual_trade_label_quantity_own = ttk.Label(self.tab_manual_frame_sell, text="Quantity:")
        self.manual_trade_label_quantity_own.grid(column=0, row=0, padx=10, pady=10)
        self.manual_trade_label_quantity_own_sum = ttk.Label(self.tab_manual_frame_sell, text="t.b.d.")
        self.manual_trade_label_quantity_own_sum.grid(column=1, row=0, padx=10, pady=10)
        self.manual_trade_label_earnings_sell = ttk.Label(self.tab_manual_frame_sell, text="Earnings:")
        self.manual_trade_label_earnings_sell.grid(column=0, row=1, padx=10, pady=10)
        self.manual_trade_entry_earnings_sell = ttk.Entry(self.tab_manual_frame_sell)
        self.manual_trade_entry_earnings_sell.grid(column=1, row=1, padx=10, pady=10)
        self.manual_trade_button_sell = ttk.Button(self.tab_manual_frame_sell, text="Sell Stock",
                                                   command=self.sell_trade)
        self.manual_trade_button_sell.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

        self.manual_trade_combobox_stockname.bind("<<ComboboxSelected>>",
                                                  self.on_manual_trade_combobox_stockname_selected)
        self.manual_trade_combobox_stockname.bind("<FocusOut>", self.on_manual_trade_combobox_stockname_selected)
        self.manual_trade_combobox_ticker.bind("<<ComboboxSelected>>", self.on_manual_trade_combobox_ticker_selected)
        self.manual_trade_combobox_ticker.bind("<FocusOut>", self.on_manual_trade_combobox_ticker_selected)
        self.update_tab_manual_trade()

    def setup_tab_statistics(self):
        """Initialisiert und konfiguriert das Tab für Statistiken."""
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

    def register_update_all_tabs(self, func):
        """Registriert eine Funktion, die aufgerufen wird, wenn alle Tabs aktualisiert werden sollen."""
        self.registered_update_functions.append(func)

    def update_all_tabs(self):
        """Aktualisiert alle Tabs der Anwendung."""
        self.update_tab_active_trades()
        self.update_tab_trade_history()
        self.update_tab_manual_trade()
        for update_function in self.registered_update_functions:
            update_function()

    def update_tab_active_trades(self):
        """Aktualisiert die Anzeige der aktiven Trades."""
        trades = self.db.get_current_stock_set()
        for item in self.treeview_active_trades.get_children():
            self.treeview_active_trades.delete(item)
        portfolio_stock_names = trades.keys()
        stock_summary = {stockname: {'id': '', 'quantity': 0, 'invest': 0} for stockname in portfolio_stock_names}
        for trade, data_array in trades.items():
            for data in data_array:
                stock_summary[trade]['quantity'] += data['quantity']
                stock_summary[trade]['invest'] += data['invest']
                stock_summary[trade]['chance'] = data['chance'] if data['chance'] is not None else ''
                stock_summary[trade]['risk'] = data['risk'] if data['risk'] is not None else ''
                stock_summary[trade]['chance_explanation'] = str(data['chance_explanation']) if data[
                                                                                                    'chance_explanation'] is not None else ''
                stock_summary[trade]['risk_explanation'] = str(data['risk_explanation']) if data[
                                                                                                'risk_explanation'] is not None else ''
        # --- Sortierung nach Spalte ---
        sort_key = self.active_trades_tab.sort
        if sort_key == "name":
            portfolio_stock_names = sorted(portfolio_stock_names)
        elif sort_key == "chance":
            portfolio_stock_names = sorted(portfolio_stock_names,
                                           key=lambda name: stock_summary[name]['chance'] if stock_summary[name][
                                                                                                 'chance'] is not None else -1,
                                           reverse=True)
        elif sort_key == "risk":
            portfolio_stock_names = sorted(portfolio_stock_names,
                                           key=lambda name: stock_summary[name]['risk'] if stock_summary[name][
                                                                                               'risk'] is not None else 101,
                                           reverse=True)
        elif sort_key == "quantity":
            portfolio_stock_names = sorted(portfolio_stock_names,
                                           key=lambda name: stock_summary[name]['quantity'],
                                           reverse=True)
        elif sort_key == "invest":
            portfolio_stock_names = sorted(portfolio_stock_names,
                                           key=lambda name: stock_summary[name]['invest'],
                                           reverse=True)
        elif sort_key == "now":
            # Berechne aktuellen Wert für jedes Stock
            now_values = {}
            for stockname in portfolio_stock_names:
                current_price, currency, rate = stockdata.get_stock_price(self.db.get_ticker_symbol(stockname))
                if current_price is not None and rate is not None:
                    now_values[stockname] = stock_summary[stockname]['quantity'] * current_price * rate
                elif current_price is not None:
                    now_values[stockname] = stock_summary[stockname]['quantity'] * current_price
                else:
                    now_values[stockname] = 0
            portfolio_stock_names = sorted(portfolio_stock_names,
                                           key=lambda name: now_values[name],
                                           reverse=True)
        elif sort_key == "profit":
            # Berechne Profit für jedes Stock
            profit_values = {}
            for stockname in portfolio_stock_names:
                current_price, currency, rate = stockdata.get_stock_price(self.db.get_ticker_symbol(stockname))
                invest = stock_summary[stockname]['invest']
                if current_price is not None and rate is not None:
                    now = stock_summary[stockname]['quantity'] * current_price * rate
                    profit = now - invest
                elif current_price is not None:
                    now = stock_summary[stockname]['quantity'] * current_price
                    profit = now - invest
                else:
                    profit = 0
                profit_values[stockname] = profit
            portfolio_stock_names = sorted(portfolio_stock_names,
                                           key=lambda name: profit_values[name],
                                           reverse=True)
        # --- Ende Sortierung ---

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
                                                                                "end",
                                                                                values=(stockname,
                                                                                        stock_summary[stockname][
                                                                                            'chance'],
                                                                                        stock_summary[stockname][
                                                                                            'risk'],
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

                my_id = self.treeview_active_trades.insert(stock_summary[trade]['id'],
                                                           "end",
                                                           values=('📅' + data['date'].strftime(globals.DATE_FORMAT),
                                                                   "", "",
                                                                   f"{data['quantity']:.4f}",
                                                                   f"{data['invest']:.2f} {globals.CURRENCY}",
                                                                   current_value
                                                                   )
                                                           )
                self.treeview_active_trades.item(my_id, tags=(tag,))

    def update_tab_trade_history(self):
        """Aktualisiert die Anzeige der Trade-Historie."""
        trades = self.db.get_history_stock_set()
        for item in self.treeview_trade_history.get_children():
            self.treeview_trade_history.delete(item)
        portfolio_stock_names = sorted(trades.keys())
        for stockname in portfolio_stock_names:
            stock_id = self.treeview_trade_history.insert('',
                                                          "end",
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
                profit_percent_per_day = ((1 + profit_percent / 100) ** (
                        1 / days_held) - 1) * 100 if days_held > 0 else 0.0
                # Jahres prozensatz = (1 + tagesprozentsatz)^365 - 1
                profit_percent_per_year = ((
                                                   1 + profit_percent_per_day / 100) ** 365 - 1) * 100 if days_held > 0 else 0.0
                tag = 'neutral'
                if profit_eur > 0.01:
                    tag = 'profit_positive'
                elif profit_eur < -0.01:
                    tag = 'profit_negative'
                line = self.treeview_trade_history.insert(stock_id,
                                                          "end",
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

    def update_tab_manual_trade(self):
        """Aktualisiert die Anzeige und Auswahlmöglichkeiten im Tab für manuelle Trades."""
        stocknames = sorted(self.db.get_stock_set())
        self.manual_trade_combobox_stockname['values'] = stocknames
        self.manual_trade_combobox_stockname.set('')
        self.manual_trade_combobox_ticker['values'] = []
        self.manual_trade_combobox_ticker.set('')

    def update_tab_statistics(self):
        """Aktualisiert die Statistik-Anzeige für aktive und historische Trades."""
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
        self.label_statistics_active_profit.config(
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
        self.label_statistics_history_stocks.config(text=f"Different Stocks: {len(stocks)}")
        self.label_statistics_history_invest.config(text=f"Total Invest: {total_invest:.2f} {globals.CURRENCY}")
        self.label_statistics_history_exit.config(text=f"Total Exit: {total_exit:.2f} {globals.CURRENCY}")
        self.label_statistics_history_profit.config(
            text=f"Total Profit: {total_profit:.2f} {globals.CURRENCY} ({profit_percent:.2f} %)")
        self.label_statistics_history_profit_per_year.config(
            text=f"Average profit per Year: {(total_profit / total_days * 365):.2f} {globals.CURRENCY} ({avg_profit_per_year:.2f} %)")
        # Dividends Statistics
        # Not implemented yet

    def add_trade(self):
        """Fügt einen neuen Trade basierend auf den Benutzereingaben hinzu."""
        stockname = self.manual_trade_combobox_stockname.get()
        ticker_symbol = self.manual_trade_combobox_ticker.get()

        quantity = float(self.manual_trade_entry_quantity_buy.get().replace(',', '.'))
        price = float(self.manual_trade_entry_invest_buy.get().replace(',', '.'))
        trade_date = self.manual_trade_entry_date.get_date()

        print(stockname, ticker_symbol, quantity, price, trade_date)

        self.db.add_stockname_ticker(stockname, ticker_symbol)
        self.db.add_stock_trade(ticker_symbol, quantity, price, trade_date)

        self.manual_trade_entry_quantity_buy.delete(0, tk.END)
        self.manual_trade_entry_invest_buy.delete(0, tk.END)
        self.manual_trade_entry_date.set_date(datetime.date.today())

        self.update_all_tabs()

    def sell_trade(self):
        """Verkauft einen Trade basierend auf den Benutzereingaben."""
        stockname = self.manual_trade_combobox_stockname.get()
        ticker_symbol = self.manual_trade_combobox_ticker.get()

        earnings = float(self.manual_trade_entry_earnings_sell.get().replace(',', '.'))
        trade_date = self.manual_trade_entry_date.get_date()

        self.db.add_stockname_ticker(stockname, ticker_symbol)
        self.db.sell_stock(stockname, earnings, trade_date)

        self.manual_trade_entry_earnings_sell.delete(0, tk.END)
        self.manual_trade_entry_date.set_date(datetime.date.today())
        self.manual_trade_label_quantity_own_sum.set("")
        self.manual_trade_button_sell.config(state=tk.DISABLED)

        self.update_all_tabs()



    def update_ai_analysis(self):
        """Führt eine KI-Analyse für die aktuellen Aktien durch und speichert das Ergebnis."""

        def run_ai_analysis_thread(thread_ticker_symbols):
            try:
                self.active_trades_button_ai_analysis.config(state=tk.DISABLED)
                self.active_trades_button_ai_analysis.config(text="🧠💭💭💭💭")
                ai_report = daily_report.daily_report(thread_ticker_symbols)
                self.Window.after(0, lambda: handle_ai_report(ai_report))

            except Exception as e:
                def _show_error_and_reset():
                    messagebox.showerror("AI Analysis Error", f"An error occurred during AI analysis:\n{str(err_msg)}")
                    self.active_trades_button_ai_analysis.config(state=tk.NORMAL)
                    self.active_trades_button_ai_analysis.config(text="🧠stock analysis")

                err_msg = str(e)
                self.Window.after(0, _show_error_and_reset)

        def handle_ai_report(ai_report):
            if ai_report:
                self.db.add_new_analysis(ai_report)
                self.update_tab_active_trades()
            self.active_trades_button_ai_analysis.config(state=tk.NORMAL)
            self.active_trades_button_ai_analysis.config(text="🧠stock analysis")

        stocknames = self.db.get_current_stock_set()
        ticker_symbols = [(ticker, name) for name in stocknames.keys() if
                          (ticker := self.db.get_ticker_symbol(name)) is not None]
        threading.Thread(target=run_ai_analysis_thread, args=(ticker_symbols,), daemon=True).start()

    def on_stock_name_heading_click(self):
        """Sortiert die aktiven Trades nach Namen, wenn auf die Spaltenüberschrift geklickt wird."""
        self.active_trades_tab.sort = "name"
        self.update_tab_active_trades()

    def on_chance_heading_click(self):
        """Sortiert die aktiven Trades nach Chance, wenn auf die Spaltenüberschrift geklickt wird."""
        self.active_trades_tab.sort = "chance"
        self.update_tab_active_trades()

    def on_risk_heading_click(self):
        """Sortiert die aktiven Trades nach Risiko, wenn auf die Spaltenüberschrift geklickt wird."""
        self.active_trades_tab.sort = "risk"
        self.update_tab_active_trades()

    def on_quantity_heading_click(self):
        """Sortiert die aktiven Trades nach Menge, wenn auf die Spaltenüberschrift geklickt wird."""
        self.active_trades_tab.sort = "quantity"
        self.update_tab_active_trades()

    def on_invest_heading_click(self):
        """Sortiert die aktiven Trades nach Investition, wenn auf die Spaltenüberschrift geklickt wird."""
        self.active_trades_tab.sort = "invest"
        self.update_tab_active_trades()

    def on_now_heading_click(self):
        """Sortiert die aktiven Trades nach aktuellem Wert, wenn auf die Spaltenüberschrift geklickt wird."""
        self.active_trades_tab.sort = "now"
        self.update_tab_active_trades()

    def on_profit_heading_click(self):
        """Sortiert die aktiven Trades nach Gewinn, wenn auf die Spaltenüberschrift geklickt wird."""
        self.active_trades_tab.sort = "profit"
        self.update_tab_active_trades()

    def on_active_trades_motion(self, event):
        """Zeigt Tooltips für Chance- und Risiko-Spalten bei Mausbewegung an."""
        region = self.treeview_active_trades.identify("region", event.x, event.y)
        if region != "cell":
            self.active_trades_tooltip.hidetip()
            return
        col = self.treeview_active_trades.identify_column(event.x)
        if col not in ["#2", "#3"]:  # "Chance" ist die zweite Spalte, "Risk" die dritte Spalte
            self.active_trades_tooltip.hidetip()
            return
        else:
            if col == "#2":
                explanation_type = "chance_explanation"
            else:
                explanation_type = "risk_explanation"
        row_id = self.treeview_active_trades.identify_row(event.y)
        if not row_id:
            self.active_trades_tooltip.hidetip()
            return
        item = self.treeview_active_trades.item(row_id)
        stockname = item['values'][0]
        if stockname.startswith('📅'):
            parent_id = self.treeview_active_trades.parent(row_id)
            if not parent_id:
                self.active_trades_tooltip.hidetip()
                return
            parent_item = self.treeview_active_trades.item(parent_id)
            stockname = parent_item['values'][0]
        # Hole den Erklärungstext aus dem stock_summary (du musst das ggf. anpassen)
        trades = self.db.get_current_stock_set()
        if stockname in trades:
            explanation = ""
            for data in trades[stockname]:
                if data.get(explanation_type):
                    explanation = data[explanation_type]
                    break
            if explanation:
                x = self.treeview_active_trades.winfo_rootx() + event.x + 20
                y = self.treeview_active_trades.winfo_rooty() + event.y + 10
                self.active_trades_tooltip.showtip(explanation, x, y)
                return
        self.active_trades_tooltip.hidetip()

    def on_active_trades_treeview_click(self, _):
        """Öffnet die Yahoo Finance Seite für das ausgewählte Wertpapier bei Doppelklick."""
        # get ticker symbol from selected row
        selected_item = self.treeview_active_trades.selection()
        if selected_item:
            item = self.treeview_active_trades.item(selected_item)
            stockname = item['values'][0]
            if stockname != '' and not stockname.startswith('📅'):
                # open webbrowser with page https://finance.yahoo.com/quote/{Ticker}/
                ticker_symbol = self.db.get_ticker_symbol(stockname)
                if ticker_symbol is not None:
                    url = f"https://finance.yahoo.com/quote/{ticker_symbol}/"
                    webbrowser.open(url)
                    return "break"
        return None

    def on_history_trades_treeview_click(self, _):
        """Öffnet die Yahoo Finance Seite für das ausgewählte Wertpapier in der Historie bei Doppelklick."""
        # get ticker symbol from selected row
        selected_item = self.treeview_trade_history.selection()
        if selected_item:
            item = self.treeview_trade_history.item(selected_item)
            stockname = item['values'][0]
            if stockname != '' and not stockname.startswith('📅'):
                # open webbrowser with page https://finance.yahoo.com/quote/{Ticker}/
                ticker_symbol = self.db.get_ticker_symbol(stockname)
                if ticker_symbol is not None:
                    url = f"https://finance.yahoo.com/quote/{ticker_symbol}/"
                    webbrowser.open(url)
                    return "break"

    def on_manual_trade_combobox_stockname_selected(self, _):
        """Aktualisiert die Ticker-Auswahl und Buttons, wenn ein Aktienname ausgewählt wird."""
        stockname = self.manual_trade_combobox_stockname.get()
        ticker_symbols = stockdata.get_ticker_symbols_from_name(stockname)
        if ticker_symbols is None:
            self.manual_trade_combobox_ticker['values'] = []
            self.manual_trade_combobox_ticker.set('')
            # disable the buy and sell buttons
            self.manual_trade_button_buy.config(state=tk.DISABLED)
            self.manual_trade_button_sell.config(state=tk.DISABLED)
        else:
            self.manual_trade_combobox_ticker['values'] = ticker_symbols
            if len(ticker_symbols) > 0:
                used_symbol = self.db.get_ticker_symbol(stockname)
                if used_symbol in ticker_symbols:
                    self.manual_trade_combobox_ticker.set(used_symbol)
                    quantity = self.db.get_quantity_of_stock(stockname)
                    if quantity and quantity > 0:
                        self.manual_trade_label_quantity_own_sum.config(text=f"{quantity:.4f}")
                        # enable the buy and sell buttons
                        self.manual_trade_button_buy.config(state=tk.NORMAL)
                        self.manual_trade_button_sell.config(state=tk.NORMAL)
                    else:
                        self.manual_trade_label_quantity_own_sum.config(text="")
                        # enable only the buy button
                        self.manual_trade_button_buy.config(state=tk.NORMAL)
                        self.manual_trade_button_sell.config(state=tk.DISABLED)
                else:
                    self.manual_trade_combobox_ticker.set(ticker_symbols[0])
                    self.manual_trade_label_quantity_own_sum.config(text="")
                    self.manual_trade_button_buy.config(state=tk.NORMAL)
                    self.manual_trade_button_sell.config(state=tk.DISABLED)

    def on_manual_trade_combobox_ticker_selected(self, _):
        """Aktualisiert die Anzeige und Buttons, wenn ein Ticker ausgewählt wird."""
        ticker_symbol = self.manual_trade_combobox_ticker.get()
        stockname = self.db.get_stockname(ticker_symbol)
        if stockname is not None:
            self.manual_trade_combobox_stockname.set(stockname)
            # enable the buy and sell buttons
            self.manual_trade_button_buy.config(state=tk.NORMAL)
            self.manual_trade_button_sell.config(state=tk.NORMAL)
            quantity = self.db.get_quantity_of_stock(stockname)
            if quantity and quantity > 0:
                self.manual_trade_label_quantity_own_sum.config(text=f"{quantity:.4f}")
                # enable the buy and sell buttons
                self.manual_trade_button_buy.config(state=tk.NORMAL)
                self.manual_trade_button_sell.config(state=tk.NORMAL)
            else:
                self.manual_trade_label_quantity_own_sum.config(text="")
                # enable only the buy button
                self.manual_trade_button_buy.config(state=tk.NORMAL)
                self.manual_trade_button_sell.config(state=tk.DISABLED)
        else:
            self.manual_trade_button_buy.config(state=tk.DISABLED)
            self.manual_trade_button_sell.config(state=tk.DISABLED)

    def on_add_combobox_stockname_selected(self, _):
        """Aktualisiert die Ticker-Auswahl im Hinzufügen-Dialog, wenn ein Aktienname ausgewählt wird."""
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



    def start_auto_update(self):
        """Startet das automatische Update für aktive Trades alle 5 Minuten."""
        # Schedule the first update
        self.schedule_auto_update()

    def schedule_auto_update(self):
        """Plant das nächste automatische Update ein."""
        # Update every 5 minutes (300,000 milliseconds)
        update_interval = 5 * 60 * 1000  # 5 minutes in milliseconds
        self.auto_update_job = self.Window.after(update_interval, self.perform_auto_update)

    def perform_auto_update(self):
        """Führt das automatische Update der aktiven Trades durch."""
        try:
            # Update the active trades tab
            self.update_tab_active_trades()
        except Exception as e:
            print(f"Auto-update failed: {e}")
        finally:
            # Schedule the next update
            self.schedule_auto_update()

    def stop_auto_update(self):
        """Stoppt das automatische Update."""
        if self.auto_update_job is not None:
            self.Window.after_cancel(self.auto_update_job)
            self.auto_update_job = None

    def run(self):
        """Startet die Haupt-Event-Loop der Anwendung."""
        try:
            self.Window.mainloop()
        finally:
            # Clean up auto-update timer when application closes
            self.stop_auto_update()
            globals.save_user_config()

