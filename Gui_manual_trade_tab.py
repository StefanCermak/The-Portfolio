import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import datetime

import stockdata
import Db


class ManualTradeTab:
    def __init__(self, parent, update_all_tabs_callback, register_update_all_tabs):
        """Initialisiert das Tab für manuelle Trades."""
        self.db = Db.Db()
        self.update_all_tabs = update_all_tabs_callback
        register_update_all_tabs(self.update_tab_manual_trade)

        self.tab_manual_frame_common = ttk.Frame(parent)
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
        self.tab_manual_frame_buy = ttk.LabelFrame(parent, text="Buy Stock")
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
        self.tab_manual_frame_sell = ttk.LabelFrame(parent, text="Sell Stock")
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

    def update_tab_manual_trade(self):
        """Aktualisiert die Anzeige und Auswahlmöglichkeiten im Tab für manuelle Trades."""
        tickers_with_stockname = self.db.get_stocknames_with_tickers()
        stocknames = sorted(tickers_with_stockname.values())
        tickers = sorted(tickers_with_stockname.keys())
        self.manual_trade_combobox_stockname['values'] = stocknames
        self.manual_trade_combobox_stockname.set('')
        self.manual_trade_combobox_ticker['values'] = tickers
        self.manual_trade_combobox_ticker.set('')

    def add_trade(self):
        """Fügt einen neuen Trade basierend auf den Benutzereingaben hinzu."""
        stockname = self.manual_trade_combobox_stockname.get()
        ticker_symbol = self.manual_trade_combobox_ticker.get()
        try:
            quantity = float(self.manual_trade_entry_quantity_buy.get().replace(',', '.'))
            price = float(self.manual_trade_entry_invest_buy.get().replace(',', '.'))
        except Exception:
            return
        trade_date = self.manual_trade_entry_date.get_date()
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
        try:
            earnings = float(self.manual_trade_entry_earnings_sell.get().replace(',', '.'))
        except Exception:
            return
        trade_date = self.manual_trade_entry_date.get_date()
        self.db.add_stockname_ticker(stockname, ticker_symbol)
        self.db.sell_stock(stockname, earnings, trade_date)
        self.manual_trade_entry_earnings_sell.delete(0, tk.END)
        self.manual_trade_entry_date.set_date(datetime.date.today())
        self.manual_trade_label_quantity_own_sum.config(text="")
        self.manual_trade_button_sell.config(state=tk.DISABLED)
        self.update_all_tabs()

    def on_manual_trade_combobox_stockname_selected(self, _):
        """Aktualisiert die Ticker-Auswahl und Buttons, wenn ein Aktienname ausgewählt wird."""
        stockname = self.manual_trade_combobox_stockname.get()
        tickers_with_stockname = self.db.get_stocknames_with_tickers()
        if stockname in tickers_with_stockname.values():
            self.manual_trade_combobox_ticker['values'] = list(tickers_with_stockname.keys())
            ticker = None
            for t, s in tickers_with_stockname.items():
                if s == stockname:
                    ticker = t
                    break
            self.manual_trade_combobox_ticker.set(ticker)
            quantity = self.db.get_quantity_of_stock(stockname)
            if quantity and quantity > 0:
                self.manual_trade_label_quantity_own_sum.config(text=f"{quantity:.4f}")
                self.manual_trade_button_buy.config(state=tk.NORMAL)
                self.manual_trade_button_sell.config(state=tk.NORMAL)
            else:
                self.manual_trade_label_quantity_own_sum.config(text="")
                self.manual_trade_button_buy.config(state=tk.NORMAL)
                self.manual_trade_button_sell.config(state=tk.DISABLED)
        else:
            ticker_symbols = stockdata.get_ticker_symbols_from_name(stockname)
            if ticker_symbols is None:
                self.manual_trade_combobox_ticker['values'] = []
                self.manual_trade_combobox_ticker.set('')
                self.manual_trade_button_buy.config(state=tk.DISABLED)
                self.manual_trade_button_sell.config(state=tk.DISABLED)
            else:
                self.manual_trade_combobox_ticker['values'] = ticker_symbols
                if len(ticker_symbols) > 0:
                    self.manual_trade_combobox_ticker.set('')
                    self.manual_trade_label_quantity_own_sum.config(text="")
                    self.manual_trade_button_buy.config(state=tk.NORMAL)
                    self.manual_trade_button_sell.config(state=tk.DISABLED)

    def on_manual_trade_combobox_ticker_selected(self, _):
        """Aktualisiert die Anzeige und Buttons, wenn ein Ticker ausgewählt wird."""
        ticker_symbol = self.manual_trade_combobox_ticker.get()
        stockname = self.db.get_stockname(ticker_symbol)
        if stockname is None:
            self.manual_trade_label_quantity_own_sum.config(text="")
            self.manual_trade_button_buy.config(state=tk.NORMAL)
            self.manual_trade_button_sell.config(state=tk.DISABLED)
        else:
            self.manual_trade_combobox_stockname.set(stockname)
            quantity = self.db.get_quantity_of_stock(stockname)
            if quantity and quantity > 0:
                self.manual_trade_label_quantity_own_sum.config(text=f"{quantity:.4f}")
                self.manual_trade_button_buy.config(state=tk.NORMAL)
                self.manual_trade_button_sell.config(state=tk.NORMAL)
            else:
                self.manual_trade_label_quantity_own_sum.config(text="")
                self.manual_trade_button_buy.config(state=tk.NORMAL)
                self.manual_trade_button_sell.config(state=tk.DISABLED)



