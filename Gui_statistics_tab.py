import tkinter.ttk as ttk
import globals
import stockdata
import Db


class StatisticsTab:
    def __init__(self, parent, register_update_all_tabs):
        """Initialisiert das Statistik-Tab mit allen Statistiken."""
        self.db = Db.Db()
        register_update_all_tabs(self.update_tab_statistics)

        self.frame_active = ttk.LabelFrame(parent, text="Active Trades Statistics")
        self.frame_active.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")
        self.frame_history = ttk.LabelFrame(parent, text="Trade History Statistics")
        self.frame_history.grid(column=1, row=0, padx=10, pady=10, sticky="nsew")
        self.frame_dividends = ttk.LabelFrame(parent, text="Dividends Statistics")
        self.frame_dividends.grid(column=2, row=0, padx=10, pady=10, sticky="nsew")

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

        self.update_tab_statistics()

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
