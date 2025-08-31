import tkinter as tk
import tkinter.ttk as ttk
from tkcalendar import DateEntry

import datetime

import globals
import Db


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
            columns=("Stock Name", "Quantity", "Invest", "Now"),
            show='tree headings'
        )
        self.treeview_active_trades.heading("Stock Name", text="Stock Name")
        self.treeview_active_trades.heading("Quantity", text="Quantity")
        self.treeview_active_trades.heading("Invest", text="Invest")
        self.treeview_active_trades.heading("Now", text="Now")
        self.treeview_active_trades.column("#0", width=30, stretch=False)
        self.treeview_active_trades.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")

        self.update_tab_active_trades()

    def setup_tab_trade_history(self):
        self.trade_history_tab.columnconfigure(0, weight=1)
        self.trade_history_tab.rowconfigure(0, weight=1)
        self.treeview_trade_history = ttk.Treeview(
            self.trade_history_tab,
            columns=("Stock Name", "Start Date", "End Date", "Sum Buy", "Sum Sell"),
            show='tree headings'
        )
        self.treeview_trade_history.heading("Stock Name", text="Stock Name")
        self.treeview_trade_history.heading("Start Date", text="Start Date")
        self.treeview_trade_history.heading("End Date", text="End Date")
        self.treeview_trade_history.heading("Sum Buy", text="Sum Buy")
        self.treeview_trade_history.heading("Sum Sell", text="Sum Sell")
        self.treeview_trade_history.column("#0", width=30, stretch=False)
        self.treeview_trade_history.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")

        self.update_tab_trade_history()

    def setup_tab_add_trade(self):
        self.add_label_stockname = ttk.Label(self.add_trade_tab, text="Stock Name:")
        self.add_label_stockname.grid(column=0, row=0, padx=10, pady=10)
        self.add_combobox_stockname = ttk.Combobox(self.add_trade_tab, values=sorted(self.db.get_stock_set()))
        self.add_combobox_stockname.grid(column=1, row=0, padx=10, pady=10)
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

    def setup_tab_sell(self):
        self.sell_label_stockname = ttk.Label(self.sell_tab, text="Stock Name:")
        self.sell_label_stockname.grid(column=0, row=0, padx=10, pady=10)
        self.sell_combobox_stockname = ttk.Combobox(self.sell_tab, values=sorted(self.db.get_stock_set()))
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
        pass

    def setup_tab_settings(self):
        pass

    def setup_tab_about(self):
        pass

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
            stock_summary[stockname]['id'] = self.treeview_active_trades.insert('',
                                                                                tk.END,
                                                                                values=(stockname,
                                                                                        f"{stock_summary[stockname]['quantity']:.4f}",
                                                                                        f"{stock_summary[stockname]['invest']:.2f} {globals.CURRENCY}",
                                                                                        "0.00 " + globals.CURRENCY  # Placeholder for current value
                                                                                        )
                                                                                )
        for trade, data_array in trades.items():
            sorted_data_array = sorted(data_array, key=lambda d: d['date'], reverse=True)
            for data in sorted_data_array:
                self.treeview_active_trades.insert(stock_summary[trade]['id'],
                                                   tk.END,
                                                   values=('📅'+data['date'].strftime(globals.DATE_FORMAT),
                                                           f"{data['quantity']:.4f}",
                                                           f"{data['invest']:.2f} {globals.CURRENCY}",
                                                           "0.00 " + globals.CURRENCY  # Placeholder for current value
                                                           )
                                                )

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
            for data in sorted_data_array:
                self.treeview_trade_history.insert(stock_id,
                                                  tk.END,
                                                  values=(
                                                      '',
                                                      data['start_date'].strftime(globals.DATE_FORMAT),
                                                      data['end_date'].strftime(globals.DATE_FORMAT),
                                                      f"{data['sum_buy']:.2f} {globals.CURRENCY}",
                                                      f"{data['sum_sell']:.2f} {globals.CURRENCY}"
                                                  )
                                                  )

    def update_tab_add_trade(self):
        stocknames = sorted(self.db.get_stock_set())
        self.add_combobox_stockname['values'] = stocknames

    def update_tab_sell(self):
        stocknames = sorted(self.db.get_stock_set())
        self.sell_combobox_stockname['values'] = stocknames

    def add_trade(self):
        stockname = self.add_combobox_stockname.get()
        quantity = float(self.add_entry_quantity.get().replace(',', '.'))
        price = float(self.add_entry_invest.get().replace(',', '.'))
        trade_date = self.add_entry_date.get_date()

        self.db.add_stock_trade(stockname, quantity, price, trade_date)

        self.add_combobox_stockname.set('')
        self.add_entry_quantity.delete(0, tk.END)
        self.add_entry_invest.delete(0, tk.END)
        self.add_entry_date.set_date(datetime.date.today())

        self.update_tab_add_trade()
        self.update_tab_active_trades()
        self.update_tab_sell()

    def sell_trade(self):
        stockname = self.sell_combobox_stockname.get()
        earnings = float(self.sell_entry_earnings.get().replace(',', '.'))
        sell_date = self.sell_entry_date.get_date()

        self.db.sell_stock(stockname, earnings, sell_date)

        self.sell_combobox_stockname.set('')
        self.sell_entry_earnings.delete(0, tk.END)
        self.sell_entry_date.set_date(datetime.date.today())

        self.update_tab_add_trade()
        self.update_tab_active_trades()
        self.update_tab_sell()

    def run(self):
        self.Window.mainloop()
        globals.save_user_config()
