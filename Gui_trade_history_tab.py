import tkinter.ttk as ttk
import webbrowser

import globals
import Db


class TradeHistoryTab:
    """
    Tab for displaying and managing the trade history of stocks in the portfolio.
    Provides an overview of completed trades, including profits and performance metrics.
    """
    def __init__(self, parent, register_update_all_tabs):
        """
        Initialize the TradeHistoryTab.

        Args:
            parent: The parent tkinter widget.
            register_update_all_tabs: Function to register the update callback.
        """
        self.db = Db.Db()
        register_update_all_tabs(self.update_tab_trade_history)

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        self.treeview_trade_history = ttk.Treeview(
            parent,
            columns=("Stock Name", "Start Date", "End Date", "Sum Buy", "Sum Sell", "Profit", "Profit %",
                     "Profit %(Year)"),
            show='tree headings'
        )
        self.treeview_trade_history.heading("Stock Name", text="Stock Name")
        self.treeview_trade_history.heading("Start Date", text="Start Date")
        self.treeview_trade_history.heading("End Date", text="End Date")
        self.treeview_trade_history.heading("Sum Buy", text="Sum Buy")
        self.treeview_trade_history.heading("Sum Sell", text="Sum Sell")
        self.treeview_trade_history.heading("Profit", text="Profit")
        self.treeview_trade_history.heading("Profit %", text="Profit %")
        self.treeview_trade_history.heading("Profit %(Year)", text="Profit %(Year)")
        self.treeview_trade_history.column("#0", width=30, stretch=False)
        self.treeview_trade_history.column("Start Date", width=100, stretch=False)
        self.treeview_trade_history.column("End Date", width=100, stretch=False)
        self.treeview_trade_history.column("Sum Buy", width=120, stretch=False)
        self.treeview_trade_history.column("Sum Sell", width=120, stretch=False)
        self.treeview_trade_history.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")
        self.treeview_trade_history.tag_configure('profit_positive', foreground='green')
        self.treeview_trade_history.tag_configure('profit_negative', foreground='red')
        self.treeview_trade_history.tag_configure('neutral', foreground='blue')

        self.treeview_trade_history.bind("<Double-Button-1>", self.on_history_trades_treeview_click)

        self.update_tab_trade_history()

    def update_tab_trade_history(self):
        """
        Refreshes the trade history table with completed trades from the database.
        Calculates profit and performance metrics for each trade and updates the treeview.
        """
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
                profit_percent_per_day = ((1 + profit_percent / 100) ** (
                        1 / days_held) - 1) * 100 if days_held > 0 else 0.0
                profit_percent_per_year = ((
                                                       1 + profit_percent_per_day / 100) ** 365 - 1) * 100 if days_held > 0 else 0.0
                tag = 'neutral'
                if profit_eur > globals.PROFIT_THRESHOLD:
                    tag = 'profit_positive'
                elif profit_eur < -globals.PROFIT_THRESHOLD:
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
            if sum_profit > globals.PROFIT_THRESHOLD:
                tag = 'profit_positive'
            elif sum_profit < -globals.PROFIT_THRESHOLD:
                tag = 'profit_negative'
            self.treeview_trade_history.item(stock_id, tags=(tag,))

    def on_history_trades_treeview_click(self, _):
        """
        Opens the Yahoo Finance page for the selected stock in the trade history on double-click.

        Args:
            _: The tkinter event object (unused).
        Returns:
            "break" if a stock link was opened, otherwise None.
        """
        selected_item = self.treeview_trade_history.selection()
        if selected_item:
            item = self.treeview_trade_history.item(selected_item)
            stockname = item['values'][0]
            if stockname != '' and not stockname.startswith('📅'):
                ticker_symbol = self.db.get_ticker_symbol(stockname)
                if ticker_symbol is not None:
                    url = f"https://finance.yahoo.com/quote/{ticker_symbol}/"
                    webbrowser.open(url)
                    return "break"
