import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import webbrowser
import threading
from typing import Callable, Any

import globals
import Db
import stockdata
import tools
import ai_risk_and_chance_analysis


class ActiveTradesTab:
    """
    Tab for displaying and managing active stock trades in the portfolio.
    Provides sorting, AI analysis, and tooltips for additional information.
    """
    def __init__(
        self,
        parent: tk.Widget,
        update_all_tabs_callback: Callable[[], None],
        register_update_all_tabs: Callable[[Callable[[], None]], None]
    ) -> None:
        """
        Initialize the ActiveTradesTab.

        Args:
            parent: The parent tkinter widget.
            update_all_tabs_callback: Callback to update all tabs.
            register_update_all_tabs: Function to register the update callback.
        """
        self.db = Db.Db()
        self.update_all_tabs = update_all_tabs_callback
        register_update_all_tabs(self.update_tab_active_trades)

        parent.sort = "name"
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=0)
        parent.rowconfigure(1, weight=1)

        self.menu_frame = ttk.Frame(parent)
        self.menu_frame.grid(column=0, row=0, padx=0, pady=0, sticky="nsew")
        self.button_ai_analysis = ttk.Button(self.menu_frame, text="🧠stock analysis",
                                             command=self.update_ai_analysis)
        self.button_ai_analysis.grid(column=0, row=0, padx=0, pady=0)

        self.treeview = ttk.Treeview(
            parent,
            columns=("Stock Name", "Chance", "Risk", "Quantity", "Invest", "Now", "Profit"),
            show='tree headings'
        )
        self.treeview.heading("Stock Name", text="Stock Name", command=self.on_stock_name_heading_click)
        self.treeview.heading("Chance", text="++", command=self.on_chance_heading_click)
        self.treeview.heading("Risk", text="--", command=self.on_risk_heading_click)
        self.treeview.heading("Quantity", text="Quantity", command=self.on_quantity_heading_click)
        self.treeview.heading("Invest", text="Invest", command=self.on_invest_heading_click)
        self.treeview.heading("Now", text="Now", command=self.on_now_heading_click)
        self.treeview.heading("Profit", text="Profit", command=self.on_profit_heading_click)
        self.treeview.column("#0", width=30, stretch=False)
        self.treeview.column("Quantity", width=120, stretch=False)
        self.treeview.column("Chance", width=30, stretch=False)
        self.treeview.column("Risk", width=30, stretch=False)
        self.treeview.column("Invest", width=150, stretch=False)
        self.treeview.column("Now", width=200, stretch=False)
        self.treeview.column("Profit", width=200, stretch=False)

        self.treeview.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
        self.treeview.tag_configure('profit_positive', foreground='green')
        self.treeview.tag_configure('profit_negative', foreground='red')
        self.treeview.tag_configure('neutral', foreground='blue')
        self.treeview.bind("<Double-Button-1>", self.on_treeview_click)
        self.treeview.bind("<Motion>", self.on_treeview_motion)
        self.treeview.bind("<Leave>", lambda e: self.tooltip.hidetip())

        self.tooltip = tools.ToolTip(self.treeview)
        self.update_tab_active_trades()

    def update_tab_active_trades(self) -> None:
        """
        Refreshes the active trades table with current portfolio data.
        Applies sorting and updates the treeview with latest values.
        """
        trades = self.db.get_current_stock_set()
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        portfolio_stock_names = trades.keys()
        stock_summary = {stockname: {'id': '', 'quantity': 0, 'invest': 0} for stockname in portfolio_stock_names}
        for trade, data_array in trades.items():
            for data in data_array:
                stock_summary[trade]['quantity'] += data['quantity']
                stock_summary[trade]['invest'] += data['invest']
                stock_summary[trade]['chance'] = data['chance'] if data['chance'] is not None else ''
                stock_summary[trade]['risk'] = data['risk'] if data['risk'] is not None else ''
                stock_summary[trade]['chance_explanation'] = str(data['chance_explanation']) if data['chance_explanation'] is not None else ''
                stock_summary[trade]['risk_explanation'] = str(data['risk_explanation']) if data['risk_explanation'] is not None else ''
        sort_key = self.treeview.master.sort
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
                if earnings_eur > globals.PROFIT_THRESHOLD:
                    tag = 'profit_positive'
                elif earnings_eur < -globals.PROFIT_THRESHOLD:
                    tag = 'profit_negative'

            stock_summary[stockname]['id'] = self.treeview.insert('',
                                                                  "end",
                                                                  values=(stockname,
                                                                          stock_summary[stockname]['chance'],
                                                                          stock_summary[stockname]['risk'],
                                                                          f"{stock_summary[stockname]['quantity']:.4f}",
                                                                          f"{stock_summary[stockname]['invest']:.2f} {globals.CURRENCY}",
                                                                          current_value,
                                                                          profit_text
                                                                          )
                                                                  )
            self.treeview.item(stock_summary[stockname]['id'], tags=(tag,))

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
                    if earnings_eur > globals.PROFIT_THRESHOLD:
                        tag = 'profit_positive'
                    elif earnings_eur < -globals.PROFIT_THRESHOLD:
                        tag = 'profit_negative'

                my_id = self.treeview.insert(stock_summary[trade]['id'],
                                             "end",
                                             values=('📅' + data['date'].strftime(globals.DATE_FORMAT),
                                                     "", "",
                                                     f"{data['quantity']:.4f}",
                                                     f"{data['invest']:.2f} {globals.CURRENCY}",
                                                     current_value
                                                     )
                                             )
                self.treeview.item(my_id, tags=(tag,))

    def update_ai_analysis(self) -> None:
        """
        Triggers AI-based stock analysis for all current portfolio stocks.
        Updates the database and refreshes the table with new analysis results.
        """
        def run_ai_analysis_thread(thread_ticker_symbols):
            try:
                self.button_ai_analysis.config(state=tk.DISABLED)
                self.button_ai_analysis.config(text="🧠💭💭💭💭")
                ai_report = ai_risk_and_chance_analysis.get_Report(thread_ticker_symbols)
                self.treeview.after(0, lambda: handle_ai_report(ai_report))
            except Exception as e:
                def _show_error_and_reset():
                    messagebox.showerror("AI Analysis Error", f"An error occurred during AI analysis:\n{str(err_msg)}")
                    self.button_ai_analysis.config(state=tk.NORMAL)
                    self.button_ai_analysis.config(text="🧠stock analysis")

                err_msg = str(e)
                self.treeview.after(0, _show_error_and_reset)

        def handle_ai_report(ai_report):
            if ai_report:
                self.db.add_new_analysis(ai_report)
                self.update_tab_active_trades()
            self.button_ai_analysis.config(state=tk.NORMAL)
            self.button_ai_analysis.config(text="🧠stock analysis")

        stock_names = self.db.get_current_stock_set()
        ticker_symbols = [(ticker, name) for name in stock_names.keys() if
                          (ticker := self.db.get_ticker_symbol(name)) is not None]
        threading.Thread(target=run_ai_analysis_thread, args=(ticker_symbols,), daemon=True).start()

    def on_stock_name_heading_click(self) -> None:
        """
        Sorts the table by stock name when the column header is clicked.
        """
        self.treeview.master.sort = "name"
        self.update_tab_active_trades()

    def on_chance_heading_click(self) -> None:
        """
        Sorts the table by chance value when the column header is clicked.
        """
        self.treeview.master.sort = "chance"
        self.update_tab_active_trades()

    def on_risk_heading_click(self) -> None:
        """
        Sorts the table by risk value when the column header is clicked.
        """
        self.treeview.master.sort = "risk"
        self.update_tab_active_trades()

    def on_quantity_heading_click(self) -> None:
        """
        Sorts the table by quantity when the column header is clicked.
        """
        self.treeview.master.sort = "quantity"
        self.update_tab_active_trades()

    def on_invest_heading_click(self) -> None:
        """
        Sorts the table by invested amount when the column header is clicked.
        """
        self.treeview.master.sort = "invest"
        self.update_tab_active_trades()

    def on_now_heading_click(self) -> None:
        """
        Sorts the table by current value when the column header is clicked.
        """
        self.treeview.master.sort = "now"
        self.update_tab_active_trades()

    def on_profit_heading_click(self) -> None:
        """
        Sorts the table by profit when the column header is clicked.
        """
        self.treeview.master.sort = "profit"
        self.update_tab_active_trades()

    def on_treeview_motion(self, event: tk.Event) -> None:
        """
        Handles mouse movement over the treeview.
        Shows tooltips for chance/risk explanations when hovering over relevant cells.

        Args:
            event: The tkinter event object.
        """
        region = self.treeview.identify("region", event.x, event.y)
        if region != "cell":
            self.tooltip.hidetip()
            return
        col = self.treeview.identify_column(event.x)
        if col not in ["#2", "#3"]:
            self.tooltip.hidetip()
            return
        else:
            if col == "#2":
                explanation_type = "chance_explanation"
            else:
                explanation_type = "risk_explanation"
        row_id = self.treeview.identify_row(event.y)
        if not row_id:
            self.tooltip.hidetip()
            return
        item = self.treeview.item(row_id)
        stockname = item['values'][0]
        if stockname.startswith('📅'):
            parent_id = self.treeview.parent(row_id)
            if not parent_id:
                self.tooltip.hidetip()
                return
            parent_item = self.treeview.item(parent_id)
            stockname = parent_item['values'][0]
        trades = self.db.get_current_stock_set()
        if stockname in trades:
            explanation = ""
            for data in trades[stockname]:
                if data.get(explanation_type):
                    explanation = data[explanation_type]
                    break
            if explanation:
                x = self.treeview.winfo_rootx() + event.x + 20
                y = self.treeview.winfo_rooty() + event.y + 10
                self.tooltip.showtip(explanation, x, y)
                return
        self.tooltip.hidetip()

    def on_treeview_click(self, _: Any) -> str | None:
        """
        Handles double-clicks on the treeview.
        Opens the Yahoo Finance page for the selected stock.

        Args:
            _: The tkinter event object (unused).
        Returns:
            "break" if a stock link was opened, otherwise None.
        """
        selected_item = self.treeview.selection()
        if selected_item:
            item = self.treeview.item(selected_item)
            stockname = item['values'][0]
            if stockname != '' and not stockname.startswith('📅'):
                ticker_symbol = self.db.get_ticker_symbol(stockname)
                if ticker_symbol is not None:
                    url = f"https://finance.yahoo.com/quote/{ticker_symbol}/"
                    webbrowser.open(url)
                    return "break"
        return None
