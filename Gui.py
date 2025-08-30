import tkinter as tk
import tkinter.ttk as ttk


class BrokerApp:
    def __init__(self):
        self.Window = tk.Tk()
        self.Window.title("Broker Application")
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

    def run(self):
        self.Window.mainloop()

