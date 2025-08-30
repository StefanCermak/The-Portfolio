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
        self.tab_control.add(self.sell_tab, text='Sell')
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
        pass

    def setup_tab_trade_history(self):
        pass

    def setup_tab_add_trade(self):
        self.add_label_stockname = ttk.Label(self.add_trade_tab, text="Stock Name:")
        self.add_label_stockname.grid(column=0, row=0, padx=10, pady=10)
        self.add_combobox_stockname = ttk.Combobox(self.add_trade_tab, values=sorted(self.db.get_stock_set()))
        self.add_combobox_stockname.grid(column=1, row=0, padx=10, pady=10)
        self.add_label_quantity = ttk.Label(self.add_trade_tab, text="Quantity:")
        self.add_label_quantity.grid(column=0, row=1, padx=10, pady=10)
        self.add_entry_quantity = ttk.Entry(self.add_trade_tab)
        self.add_entry_quantity.grid(column=1, row=1, padx=10, pady=10)
        self.add_label_price = ttk.Label(self.add_trade_tab, text="Price:")
        self.add_label_price.grid(column=0, row=2, padx=10, pady=10)
        self.add_entry_price = ttk.Entry(self.add_trade_tab)
        self.add_entry_price.grid(column=1, row=2, padx=10, pady=10)
        self.add_label_date = ttk.Label(self.add_trade_tab, text="Trade Date:")
        self.add_label_date.grid(column=0, row=3, padx=10, pady=10)
        self.add_entry_date = DateEntry(self.add_trade_tab, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy',
                                        year=datetime.date.today().year, date=datetime.date.today())
        self.add_entry_date.grid(column=1, row=3, padx=10, pady=10)
        self.button_add_trade = tk.Button(self.add_trade_tab, text="Add Trade", command=self.add_trade)
        self.button_add_trade.grid(column=0, row=4, columnspan=2, padx=10, pady=10)

    def setup_tab_sell(self):
        pass

    def setup_tab_statistics(self):
        pass

    def setup_tab_settings(self):
        pass

    def setup_tab_about(self):
        pass

    def add_trade(self):
        stockname = self.add_combobox_stockname.get()
        quantity = float(self.add_entry_quantity.get().replace(',', '.'))
        price = float(self.add_entry_price.get().replace(',', '.'))
        trade_date = self.add_entry_date.get_date()

        self.db.add_stock_trade(stockname, quantity, price, trade_date)

        self.add_combobox_stockname.set('')
        self.add_entry_quantity.delete(0, tk.END)
        self.add_entry_price.delete(0, tk.END)
        self.add_entry_date.set_date(datetime.date.today())

    def run(self):
        self.Window.mainloop()
        globals.save_user_config()
