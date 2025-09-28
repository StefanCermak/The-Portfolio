import tkinter as tk
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Callable, Any
import datetime

import globals
import stockdata
import Db

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


class StockInfoTab:
    """
    Tab for displaying detailed information about individual stocks.
    Shows stock charts, current day data, and placeholders for health check and peer compare.
    """
    
    def __init__(self, parent: Any, register_update_all_tabs: Callable[[Callable[[], None]], None]) -> None:
        """
        Initialize the StockInfoTab with all components.

        Args:
            parent: The parent tkinter widget.
            register_update_all_tabs: Function to register the update callback.
        """
        self.db = Db.Db()
        register_update_all_tabs(self.update_tab_stock_info)
        
        # Main container with grid layout
        self.main_frame = ttk.Frame(parent)
        self.main_frame.grid(column=0, row=0, padx=0, pady=0, sticky="nsew")
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Configure grid weights for responsive layout
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        
        # Top frame for stock selection
        self.frame_select = ttk.LabelFrame(self.main_frame, text="Selection")
        self.frame_select.grid(column=0, row=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Stock name combobox
        self.label_stock_selection = ttk.Label(self.frame_select, text="Select Stock:")
        self.label_stock_selection.grid(column=0, row=0, padx=10, pady=5, sticky="w")
        
        self.combobox_stock_selection = ttk.Combobox(self.frame_select, values=[], state="readonly")
        self.combobox_stock_selection.grid(column=1, row=0, padx=10, pady=5, sticky="w")
        self.combobox_stock_selection.bind("<<ComboboxSelected>>", self.on_stock_selected)
        
        # Timespan combobox
        self.label_timespan_selection = ttk.Label(self.frame_select, text="Timespan:")
        self.label_timespan_selection.grid(column=2, row=0, padx=10, pady=5, sticky="w")
        
        self.combobox_timespan_selection = ttk.Combobox(self.frame_select, values=["All", "Year", "Month", "Day"], state="readonly")
        self.combobox_timespan_selection.grid(column=3, row=0, padx=10, pady=5, sticky="w")
        self.combobox_timespan_selection.set("Year")  # Default to Year
        self.combobox_timespan_selection.bind("<<ComboboxSelected>>", self.on_timespan_selected)
        
        # Row 1: Chart (left) and Day Data (right)
        self.frame_chart = ttk.LabelFrame(self.main_frame, text="Stock Chart")
        self.frame_chart.grid(column=0, row=1, padx=10, pady=5, sticky="nsew")
        
        self.frame_day_data = ttk.LabelFrame(self.main_frame, text="Current Day Data")
        self.frame_day_data.grid(column=1, row=1, padx=10, pady=5, sticky="nsew")
        
        # Row 2: Health Check (left) and Peer Compare (right)
        self.frame_health_check = ttk.LabelFrame(self.main_frame, text="Health Check Report")
        self.frame_health_check.grid(column=0, row=2, padx=10, pady=5, sticky="nsew")
        
        self.frame_peer_compare = ttk.LabelFrame(self.main_frame, text="Peer Compare")
        self.frame_peer_compare.grid(column=1, row=2, padx=10, pady=5, sticky="nsew")
        
        # Initialize chart
        self.fig, self.ax = plt.subplots(1, 1, figsize=(6, 4), dpi=80)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_chart)
        self.canvas.get_tk_widget().grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
        self.frame_chart.grid_columnconfigure(0, weight=1)
        self.frame_chart.grid_rowconfigure(0, weight=1)
        
        # Day data text widget
        self.text_day_data = tk.Text(self.frame_day_data, width=40, height=15, wrap="word")
        self.text_day_data.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
        self.frame_day_data.grid_columnconfigure(0, weight=1)
        self.frame_day_data.grid_rowconfigure(0, weight=1)
        
        # Health check text widget (placeholder)
        self.text_health_check = tk.Text(self.frame_health_check, width=40, height=15, wrap="word")
        self.text_health_check.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
        self.text_health_check.insert(tk.END, "Health Check Report\n\n(Feature coming soon)")
        self.text_health_check.config(state=tk.DISABLED)
        self.frame_health_check.grid_columnconfigure(0, weight=1)
        self.frame_health_check.grid_rowconfigure(0, weight=1)
        
        # Peer compare text widget (placeholder)
        self.text_peer_compare = tk.Text(self.frame_peer_compare, width=40, height=15, wrap="word")
        self.text_peer_compare.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
        self.text_peer_compare.insert(tk.END, "Peer Compare\n\n(Feature coming soon)")
        self.text_peer_compare.config(state=tk.DISABLED)
        self.frame_peer_compare.grid_columnconfigure(0, weight=1)
        self.frame_peer_compare.grid_rowconfigure(0, weight=1)
        
        # Initialize with current data
        self.update_tab_stock_info()
    
    def update_tab_stock_info(self) -> None:
        """
        Updates the stock info tab with current owned stocks and refreshes data.
        """
        # Get list of owned stocks
        owned_stocks = sorted(self.db.get_stock_set())
        
        # Update combobox values
        current_selection = self.combobox_stock_selection.get()
        self.combobox_stock_selection['values'] = owned_stocks
        
        # Restore selection if still valid, otherwise clear
        if current_selection in owned_stocks:
            self.combobox_stock_selection.set(current_selection)
        else:
            if owned_stocks:
                self.combobox_stock_selection.set(owned_stocks[0])
            else:
                self.combobox_stock_selection.set("")
        
        # Update display if a stock is selected
        if self.combobox_stock_selection.get():
            self.on_stock_selected(None)
    
    def on_stock_selected(self, event) -> None:
        """
        Handle stock selection from combobox and update all displays.
        
        Args:
            event: The tkinter event (can be None when called programmatically)
        """
        selected_stock = self.combobox_stock_selection.get()
        if not selected_stock:
            self.clear_displays()
            return
        
        # Get ticker symbol for the selected stock
        ticker_symbol = self.db.get_ticker_symbol(selected_stock)
        if not ticker_symbol:
            self.clear_displays()
            return
        
        # Update chart with selected timespan data
        self.update_chart(ticker_symbol)
        
        # Update day data
        self.update_day_data(ticker_symbol)
    
    def on_timespan_selected(self, event) -> None:
        """
        Handle timespan selection from combobox and update chart display.
        
        Args:
            event: The tkinter event (can be None when called programmatically)
        """
        # Update chart if a stock is selected
        selected_stock = self.combobox_stock_selection.get()
        if selected_stock:
            ticker_symbol = self.db.get_ticker_symbol(selected_stock)
            if ticker_symbol:
                self.update_chart(ticker_symbol)
    
    def update_chart(self, ticker_symbol: str) -> None:
        """
        Update the matplotlib chart with stock data based on selected timespan.
        
        Args:
            ticker_symbol: The ticker symbol to fetch data for
        """
        try:
            # Get selected timespan
            timespan = self.combobox_timespan_selection.get()
            
            # Fetch data based on timespan
            data = None
            title_suffix = ""
            
            if timespan == "All":
                data = stockdata.get_stock_all_data(ticker_symbol)
                title_suffix = "All Available Data"
            elif timespan == "Year":
                data = stockdata.get_stock_year_data(ticker_symbol)
                title_suffix = "Last Year"
            elif timespan == "Month":
                data = stockdata.get_stock_month_data(ticker_symbol)
                title_suffix = "Last Month"
            elif timespan == "Day":
                data = stockdata.get_stock_day_chart_data(ticker_symbol)
                title_suffix = "Today (Intraday)"
            else:
                # Default to year if something goes wrong
                data = stockdata.get_stock_year_data(ticker_symbol)
                title_suffix = "Last Year"
            
            self.ax.clear()
            
            if data and data.get('dates') and data.get('prices'):
                dates = data['dates']
                prices = data['prices']
                
                self.ax.plot(dates, prices, linewidth=2, color='blue')
                self.ax.set_title(f"{ticker_symbol} - {title_suffix}")
                self.ax.set_xlabel("Date")
                self.ax.set_ylabel("Price")
                self.ax.grid(True, alpha=0.3)
                
                # Format x-axis dates
                self.fig.autofmt_xdate()
            else:
                self.ax.text(0.5, 0.5, f'No data available for {ticker_symbol}', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=self.ax.transAxes, fontsize=12)
                self.ax.set_title(f"{ticker_symbol} - No Data")
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating chart for {ticker_symbol}: {e}")
            self.ax.clear()
            self.ax.text(0.5, 0.5, f'Error loading data for {ticker_symbol}', 
                       horizontalalignment='center', verticalalignment='center', 
                       transform=self.ax.transAxes, fontsize=12)
            self.ax.set_title(f"{ticker_symbol} - Error")
            self.canvas.draw()
    
    def update_day_data(self, ticker_symbol: str) -> None:
        """
        Update the day data text widget with current day information.
        
        Args:
            ticker_symbol: The ticker symbol to fetch data for
        """
        try:
            day_data = stockdata.get_stock_day_data(ticker_symbol)
            
            self.text_day_data.config(state=tk.NORMAL)
            self.text_day_data.delete(1.0, tk.END)
            
            if day_data:
                content = f"Current Day Data for {ticker_symbol}\n"
                content += f"{'='*40}\n\n"
                content += f"Open:         {self.format_value(day_data.get('open'))}\n"
                content += f"High:         {self.format_value(day_data.get('high'))}\n"
                content += f"Low:          {self.format_value(day_data.get('low'))}\n"
                content += f"Close:        {self.format_value(day_data.get('close'))}\n"
                content += f"Volume:       {self.format_number(day_data.get('volume'))}\n"
                content += f"Change %:     {self.format_percent(day_data.get('change_percent'))}\n"
                content += f"\nLast updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                content = f"No current day data available for {ticker_symbol}"
            
            self.text_day_data.insert(tk.END, content)
            self.text_day_data.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error updating day data for {ticker_symbol}: {e}")
            self.text_day_data.config(state=tk.NORMAL)
            self.text_day_data.delete(1.0, tk.END)
            self.text_day_data.insert(tk.END, f"Error loading day data for {ticker_symbol}")
            self.text_day_data.config(state=tk.DISABLED)
    
    def clear_displays(self) -> None:
        """
        Clear all displays when no stock is selected.
        """
        # Clear chart
        self.ax.clear()
        self.ax.text(0.5, 0.5, 'Select a stock to view chart', 
                   horizontalalignment='center', verticalalignment='center', 
                   transform=self.ax.transAxes, fontsize=12)
        self.ax.set_title("Stock Chart")
        self.canvas.draw()
        
        # Clear day data
        self.text_day_data.config(state=tk.NORMAL)
        self.text_day_data.delete(1.0, tk.END)
        self.text_day_data.insert(tk.END, "Select a stock to view current day data")
        self.text_day_data.config(state=tk.DISABLED)
    
    def format_value(self, value) -> str:
        """Format a numeric value for display."""
        if value is None:
            return "N/A"
        try:
            return f"{float(value):.2f}"
        except (ValueError, TypeError):
            return "N/A"
    
    def format_number(self, value) -> str:
        """Format a large number for display."""
        if value is None:
            return "N/A"
        try:
            num = int(value)
            if num >= 1_000_000:
                return f"{num / 1_000_000:.1f}M"
            elif num >= 1_000:
                return f"{num / 1_000:.1f}K"
            else:
                return str(num)
        except (ValueError, TypeError):
            return "N/A"
    
    def format_percent(self, value) -> str:
        """Format a percentage value for display."""
        if value is None:
            return "N/A"
        try:
            return f"{float(value):.2f}%"
        except (ValueError, TypeError):
            return "N/A"