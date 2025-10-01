import tkinter as tk
import tkinter.ttk as ttk
from typing import Dict, List
import datetime

import globals
import Db


class DividendsTab:
    """
    Tab for displaying dividend payments in different views.
    Provides hierarchical views of dividends by year/stock or stock/year.
    """
    
    def __init__(self, parent, register_update_all_tabs):
        """
        Initialize the DividendsTab.

        Args:
            parent: The parent tkinter widget.
            register_update_all_tabs: Function to register the update callback.
        """
        self.db = Db.Db()
        register_update_all_tabs(self.update_tab_dividends)
        
        # Store current view mode
        self.view_mode = tk.StringVar(value="year")
        
        # Configure parent layout
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Create menu frame for view selection
        self.menu_frame = ttk.LabelFrame(parent, text="View Options")
        self.menu_frame.grid(column=0, row=0, padx=10, pady=10, sticky="ew")
        
        # Add radio buttons for view selection
        self.radio_year_summary = ttk.Radiobutton(
            self.menu_frame,
            text="Year Summary",
            variable=self.view_mode,
            value="year",
            command=self.on_view_mode_changed
        )
        self.radio_year_summary.grid(column=0, row=0, padx=10, pady=5)
        
        self.radio_stock_summary = ttk.Radiobutton(
            self.menu_frame,
            text="Stock Summary",
            variable=self.view_mode,
            value="stock",
            command=self.on_view_mode_changed
        )
        self.radio_stock_summary.grid(column=1, row=0, padx=10, pady=5)
        
        # Create treeview for dividends
        self.treeview_dividends = ttk.Treeview(
            parent,
            columns=("Name", "Amount", "Date"),
            show='tree headings'
        )
        self.treeview_dividends.heading("Name", text="Stock/Year")
        self.treeview_dividends.heading("Amount", text="Amount")
        self.treeview_dividends.heading("Date", text="Date")
        self.treeview_dividends.column("#0", width=30, stretch=False)
        self.treeview_dividends.column("Name", width=250)
        self.treeview_dividends.column("Amount", width=150, stretch=False)
        self.treeview_dividends.column("Date", width=150, stretch=False)
        self.treeview_dividends.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
        
        # Configure tags for formatting
        self.treeview_dividends.tag_configure('total', foreground='blue', font=('TkDefaultFont', 10, 'bold'))
        self.treeview_dividends.tag_configure('subtotal', foreground='green')
        self.treeview_dividends.tag_configure('payment', foreground='black')
        
        # Initial update
        self.update_tab_dividends()
    
    def on_view_mode_changed(self):
        """Called when the user changes the view mode."""
        self.update_tab_dividends()
    
    def update_tab_dividends(self):
        """
        Refreshes the dividends table based on the selected view mode.
        """
        # Clear existing items
        for item in self.treeview_dividends.get_children():
            self.treeview_dividends.delete(item)
        
        # Get all dividend payments from database
        payments = self.db.get_dividend_payments()
        
        if not payments:
            # No dividend data available
            self.treeview_dividends.insert('', "end", values=("No dividend data available", "", ""))
            return
        
        if self.view_mode.get() == "year":
            self._populate_year_summary(payments)
        else:
            self._populate_stock_summary(payments)
    
    def _populate_year_summary(self, payments: List[Dict]):
        """
        Populate treeview with Year → Stock → Individual dividends hierarchy.
        
        Args:
            payments: List of dividend payment dictionaries
        """
        # Organize data by year and stock
        year_data: Dict[int, Dict[str, List]] = {}
        
        for payment in payments:
            year = payment['payment_date'].year
            stockname = payment['stockname']
            amount = payment['amount']
            date = payment['payment_date']
            
            if year not in year_data:
                year_data[year] = {}
            if stockname not in year_data[year]:
                year_data[year][stockname] = []
            
            year_data[year][stockname].append({
                'amount': amount,
                'date': date
            })
        
        # Sort years in descending order
        sorted_years = sorted(year_data.keys(), reverse=True)
        
        for year in sorted_years:
            # Calculate total for year
            year_total = sum(
                payment['amount']
                for stock_payments in year_data[year].values()
                for payment in stock_payments
            )
            
            # Insert year node
            year_id = self.treeview_dividends.insert(
                '',
                "end",
                values=(str(year), f"{year_total:.2f} {globals.CURRENCY}", ""),
                tags=('total',)
            )
            
            # Sort stocks alphabetically
            sorted_stocks = sorted(year_data[year].keys())
            
            for stockname in sorted_stocks:
                stock_payments = year_data[year][stockname]
                stock_total = sum(p['amount'] for p in stock_payments)
                
                # Insert stock node under year
                stock_id = self.treeview_dividends.insert(
                    year_id,
                    "end",
                    values=(stockname, f"{stock_total:.2f} {globals.CURRENCY}", ""),
                    tags=('subtotal',)
                )
                
                # Sort payments by date (most recent first)
                sorted_payments = sorted(stock_payments, key=lambda p: p['date'], reverse=True)
                
                # Insert individual dividend payments
                for payment in sorted_payments:
                    self.treeview_dividends.insert(
                        stock_id,
                        "end",
                        values=(
                            "",
                            f"{payment['amount']:.2f} {globals.CURRENCY}",
                            payment['date'].strftime(globals.DATE_FORMAT)
                        ),
                        tags=('payment',)
                    )
    
    def _populate_stock_summary(self, payments: List[Dict]):
        """
        Populate treeview with Stock → Year → Individual dividends hierarchy.
        
        Args:
            payments: List of dividend payment dictionaries
        """
        # Organize data by stock and year
        stock_data: Dict[str, Dict[int, List]] = {}
        
        for payment in payments:
            stockname = payment['stockname']
            year = payment['payment_date'].year
            amount = payment['amount']
            date = payment['payment_date']
            
            if stockname not in stock_data:
                stock_data[stockname] = {}
            if year not in stock_data[stockname]:
                stock_data[stockname][year] = []
            
            stock_data[stockname][year].append({
                'amount': amount,
                'date': date
            })
        
        # Sort stocks alphabetically
        sorted_stocks = sorted(stock_data.keys())
        
        for stockname in sorted_stocks:
            # Calculate total for stock
            stock_total = sum(
                payment['amount']
                for year_payments in stock_data[stockname].values()
                for payment in year_payments
            )
            
            # Insert stock node
            stock_id = self.treeview_dividends.insert(
                '',
                "end",
                values=(stockname, f"{stock_total:.2f} {globals.CURRENCY}", ""),
                tags=('total',)
            )
            
            # Sort years in descending order
            sorted_years = sorted(stock_data[stockname].keys(), reverse=True)
            
            for year in sorted_years:
                year_payments = stock_data[stockname][year]
                year_total = sum(p['amount'] for p in year_payments)
                
                # Insert year node under stock
                year_id = self.treeview_dividends.insert(
                    stock_id,
                    "end",
                    values=(str(year), f"{year_total:.2f} {globals.CURRENCY}", ""),
                    tags=('subtotal',)
                )
                
                # Sort payments by date (most recent first)
                sorted_payments = sorted(year_payments, key=lambda p: p['date'], reverse=True)
                
                # Insert individual dividend payments
                for payment in sorted_payments:
                    self.treeview_dividends.insert(
                        year_id,
                        "end",
                        values=(
                            "",
                            f"{payment['amount']:.2f} {globals.CURRENCY}",
                            payment['date'].strftime(globals.DATE_FORMAT)
                        ),
                        tags=('payment',)
                    )
