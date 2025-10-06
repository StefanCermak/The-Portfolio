import tkinter as tk
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from charset_normalizer.md import lru_cache
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Callable, Any
import datetime

import globals
import stockdata
import Db
import tools
import sektor_report

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


def calculate_health(data: dict) -> float:
    """
    Berechnet eine Health-Variable basierend auf den Peer-Compare-Werten.
    Höherer Wert = gesünder.
    Bewertet: KGV, Spread, Kurslage, Marktkap., Volumen, 52W Hoch/Tief.
    """
    # Werte extrahieren
    try:
        kgv = data.get("trailingPE") or data.get("forwardPE")
        spread = None
        high = data.get("high")
        low = data.get("low")
        if high and low:
            spread = ((float(high) - float(low)) / ((float(high) + float(low)) / 2)) * 100
        kurs = data.get("close")
        fiftyTwoWeekHigh = data.get("fiftyTwoWeekHigh")
        fiftyTwoWeekLow = data.get("fiftyTwoWeekLow")
        marketCap = data.get("marketCap")
        volume = data.get("volume")
        # Health Score: 0-100
        score = 50
        # KGV: ideal 10-25, zu hoch/zu niedrig schlecht
        if kgv is not None:
            if 10 <= kgv <= 25:
                score += 15
            elif kgv < 10:
                score += 5
            elif kgv > 40:
                score -= 10
        # Spread: kleiner besser
        if spread is not None:
            if spread < 2:
                score += 10
            elif spread < 5:
                score += 5
            elif spread > 10:
                score -= 10
        # Kurslage: nah am 52W Hoch = teuer, nah am Tief = riskant, mittig = gut
        if kurs and fiftyTwoWeekHigh and fiftyTwoWeekLow:
            try:
                rel = (kurs - fiftyTwoWeekLow) / (fiftyTwoWeekHigh - fiftyTwoWeekLow)
                if 0.3 < rel < 0.7:
                    score += 10
                elif rel < 0.2 or rel > 0.8:
                    score -= 10
            except Exception:
                pass
        # Marktkap.: groß = stabiler
        if marketCap is not None:
            if marketCap > 10_000_000_000:
                score += 5
            elif marketCap < 500_000_000:
                score -= 5
        # Volumen: hoch = liquide
        if volume is not None:
            if volume > 1_000_000:
                score += 5
            elif volume < 50_000:
                score -= 5
        # Score begrenzen
        score = max(0, min(100, score))
        return score
    except Exception:
        return 0

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
        
        self.frame_day_data = ttk.LabelFrame(self.main_frame, text="Stock Overview")
        self.frame_day_data.grid(column=1, row=1, padx=10, pady=5, sticky="nsew")
        
        # Row 2: Health Check (left) and Peer Compare (right)
        self.frame_health_check = ttk.LabelFrame(self.main_frame, text="Health Check Report")
        self.frame_health_check.grid(column=0, row=2, padx=10, pady=5, sticky="nsew")
        
        self.frame_peer_compare = ttk.LabelFrame(self.main_frame, text="Peer Compare")
        self.frame_peer_compare.grid(column=1, row=2, padx=10, pady=5, sticky="nsew")
        
        # Initialize chart
        self.fig, self.ax = plt.subplots(1, 1, figsize=(4, 3), dpi=80)
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
        
        # Peer compare Treeview (statt Text)
        self.peer_compare_tree = ttk.Treeview(
            self.frame_peer_compare,
            columns=("SockName", "Spread", "Volume", "Change", "52W Hoch", "Kurs", "52W Tief", "KGV", "Marktkap.", "Health"),
            show="headings",
            height=15
        )
        self.peer_compare_tree.heading("SockName", text="SockName")
        self.peer_compare_tree.heading("Spread", text="Spread %")
        self.peer_compare_tree.heading("Volume", text="Volumen")
        self.peer_compare_tree.heading("Change", text="Change %")
        self.peer_compare_tree.heading("52W Hoch", text="52W Hoch")
        self.peer_compare_tree.heading("Kurs", text="Kurs")
        self.peer_compare_tree.heading("52W Tief", text="52W Tief")
        self.peer_compare_tree.heading("KGV", text="KGV")
        self.peer_compare_tree.heading("Marktkap.", text="Marktkap.")
        self.peer_compare_tree.heading("Health", text="Health")
        self.peer_compare_tree.column("SockName", width=200, anchor="w")
        self.peer_compare_tree.column("Spread", width=60, anchor="e")
        self.peer_compare_tree.column("Volume", width=60, anchor="e")
        self.peer_compare_tree.column("Change", width=60, anchor="e")
        self.peer_compare_tree.column("52W Hoch", width=80, anchor="e")
        self.peer_compare_tree.column("Kurs", width=80, anchor="e")
        self.peer_compare_tree.column("52W Tief", width=80, anchor="e")
        self.peer_compare_tree.column("KGV", width=60, anchor="e")
        self.peer_compare_tree.column("Marktkap.", width=90, anchor="e")
        self.peer_compare_tree.column("Health", width=60, anchor="e")
        self.peer_compare_tree.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
        self.frame_peer_compare.grid_columnconfigure(0, weight=1)
        self.frame_peer_compare.grid_rowconfigure(0, weight=1)

        # Treeview Tags für Formatierung
        self.peer_compare_tree.tag_configure("active", font=("TkDefaultFont", 10, "bold"))
        self.peer_compare_tree.tag_configure("portfolio", font=("TkDefaultFont", 10), background="#e6f7ff")
        self.peer_compare_tree.tag_configure("peer", font=("TkDefaultFont", 10), background="#ffffff")

        # ToolTip für Peer Compare
        self.peer_compare_tooltip = tools.ToolTip(self.peer_compare_tree)
        self.peer_compare_tree.bind("<Motion>", self.on_peer_compare_motion)
        self.peer_compare_tree.bind("<Leave>", lambda e: self.peer_compare_tooltip.hidetip())

        # Initialize with current data
        self.update_tab_stock_info()

    def update_peer_compare(self) -> None:
        """
        Aktualisiert die Peer-Compare-Tabelle mit Sektor-Daten.
        """
        # Treeview leeren
        for row in self.peer_compare_tree.get_children():
            self.peer_compare_tree.delete(row)

        stock_set_name = self.db.get_stock_set()
        stock_set_ticker = [self.db.get_ticker_symbol(name) for name in stock_set_name if self.db.get_ticker_symbol(name)]
        sektor_report_data = sektor_report.sektor_report(stock_set_ticker)

        stock_name = self.combobox_stock_selection.get()
        stock_ticker = self.db.get_ticker_symbol(stock_name)
        _, current_stock_sector = stockdata.get_industry_and_sector(stock_ticker)

        # Frame-Titel dynamisch setzen
        if current_stock_sector:
            self.frame_peer_compare.config(text=f"Peer Compare {current_stock_sector}")
        else:
            self.frame_peer_compare.config(text="Peer Compare")

        if not current_stock_sector or current_stock_sector not in sektor_report_data.keys():
            # Keine Daten für diesen Sektor
            return

        rows = []
        # Für jeden Peer im Sektor: Zeile einfügen
        for ticker, data in sektor_report_data[current_stock_sector].items():
            if not data:
                continue
            high = data.get("high")
            low = data.get("low")
            volume = data.get("volume")
            change = data.get("change_percent")
            fiftyTwoWeekHigh = data.get("fiftyTwoWeekHigh")
            fiftyTwoWeekLow = data.get("fiftyTwoWeekLow")
            trailingPE = data.get("trailingPE")
            forwardPE = data.get("forwardPE")
            marketCap = data.get("marketCap")
            kurs = data.get("close")  # aktueller Kurs
            # Spread-Berechnung
            try:
                spread = ((float(high) - float(low)) / ((float(high) + float(low)) / 2)) * 100 if high and low else None
            except Exception:
                spread = None
            spread_str = f"{spread:.2f}%" if spread is not None else "N/A"
            volume_str = self.format_number(volume)
            change_str = self.format_percent(change)
            fiftyTwoWeekHigh_str = self.format_value(fiftyTwoWeekHigh)
            kurs_str = self.format_value(kurs)
            fiftyTwoWeekLow_str = self.format_value(fiftyTwoWeekLow)
            kgv_str = self.format_value(trailingPE) if trailingPE is not None else self.format_value(forwardPE)
            marketCap_str = self.format_number(marketCap)
            StockName = self.db.get_stockname(ticker)

            if not StockName or StockName is None:
                StockName = stockdata.get_stock_company_name(ticker)
                if not StockName or StockName is None:
                    StockName = ticker

            # Tag bestimmen
            tags = []
            if ticker == stock_ticker:
                tags.append("active")
            if ticker in stock_set_ticker:
                tags.append("portfolio")
            else:
                tags.append("peer")
            # Health berechnen
            health = calculate_health(data)
            health_str = f"{health:.1f}"
            # Zeile sammeln
            rows.append({
                "values": (
                    StockName,
                    spread_str,
                    volume_str,
                    change_str,
                    fiftyTwoWeekHigh_str,
                    kurs_str,
                    fiftyTwoWeekLow_str,
                    kgv_str,
                    marketCap_str,
                    health_str
                ),
                "tags": tags,
                "health": health
            })
        # Sortieren nach Health absteigend
        rows.sort(key=lambda r: r["health"], reverse=True)
        # Einfügen
        for row in rows:
            self.peer_compare_tree.insert(
                "",
                "end",
                values=row["values"],
                tags=row["tags"]
            )

        # Nachträglich die aktive Zeile selektieren (optional, falls gewünscht)
        # for row in self.peer_compare_tree.get_children():
        #     vals = self.peer_compare_tree.item(row, "values")
        #     if vals and self.db.get_ticker_symbol(vals[0]) == stock_ticker:
        #         self.peer_compare_tree.selection_set(row)
        #         break

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

        self.update_peer_compare()
    
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
                self.ax.set_title(f"{ticker_symbol} - {title_suffix}", fontsize=9)
                self.ax.set_xlabel("Date", fontsize=7)
                self.ax.set_ylabel("Price", fontsize=7)
                self.ax.grid(True, alpha=0.3)
                
                # Achsenwerte kleiner darstellen
                self.ax.tick_params(axis='x', labelsize=7)
                self.ax.tick_params(axis='y', labelsize=7)

                # Custom date formatting based on timespan
                self._format_time_axis(timespan)
                
                # Format x-axis dates
                self.fig.autofmt_xdate()
            else:
                self.ax.text(0.5, 0.5, f'No data available for {ticker_symbol}', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=self.ax.transAxes, fontsize=12)
                self.ax.set_title(f"{ticker_symbol} - No Data", fontsize=9)
                self.ax.set_xlabel("Date", fontsize=7)
                self.ax.set_ylabel("Price", fontsize=7)
                self.ax.tick_params(axis='x', labelsize=7)
                self.ax.tick_params(axis='y', labelsize=7)
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating chart for {ticker_symbol}: {e}")
            self.ax.clear()
            self.ax.text(0.5, 0.5, f'Error loading data for {ticker_symbol}', 
                       horizontalalignment='center', verticalalignment='center', 
                       transform=self.ax.transAxes, fontsize=12)
            self.ax.set_title(f"{ticker_symbol} - Error", fontsize=9)
            self.ax.set_xlabel("Date", fontsize=7)
            self.ax.set_ylabel("Price", fontsize=7)
            self.ax.tick_params(axis='x', labelsize=7)
            self.ax.tick_params(axis='y', labelsize=7)
            self.canvas.draw()
    
    def _format_time_axis(self, timespan: str) -> None:
        """
        Format the x-axis time labels based on the selected timespan.
        
        Args:
            timespan: The selected timespan ("Day", "Month", "Year", "All")
        """
        try:
            if timespan == "Day":
                # Day: Show hours as axis labels
                self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))  # Every 2 hours
                self.ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))  # Every hour
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                
            elif timespan == "Month":
                # Month: Show days as axis labels (month not necessary as it's clear)
                self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # Every 5 days
                self.ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))  # Every day
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
                
            elif timespan == "Year":
                # Year: Show months as axis labels (all 12 months should be there)
                self.ax.xaxis.set_major_locator(mdates.MonthLocator())  # Every month
                self.ax.xaxis.set_minor_locator(mdates.WeekdayLocator())  # Every week
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  # Short month names
                
            elif timespan == "All":
                # All: Show only year transitions (not every year needs to be shown)
                self.ax.xaxis.set_major_locator(mdates.YearLocator())  # Every year
                self.ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[1, 7]))  # Jan and July
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                
        except Exception as e:
            print(f"Warning: Could not format time axis for {timespan}: {e}")
            # Fallback to default formatting
            self.fig.autofmt_xdate()
    
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
                content = f"Stock Overview for {ticker_symbol}\n"
                content += f"{'='*40}\n\n"
                content += f"Open:               {self.format_value(day_data.get('open'))} {day_data.get('currency') or 'N/A'}\n"
                content += f"High:               {self.format_value(day_data.get('high'))} {day_data.get('currency') or 'N/A'}\n"
                content += f"Low:                {self.format_value(day_data.get('low'))} {day_data.get('currency') or 'N/A'}\n"
                content += f"Close:              {self.format_value(day_data.get('close'))} {day_data.get('currency') or 'N/A'}\n"
                content += f"Volume:             {self.format_number(day_data.get('volume'))}\n"
                content += f"Change %:           {self.format_percent(day_data.get('change_percent'))}\n"
                content += f"Dividend Yield:     {self.format_percent(day_data.get('dividend_yield'))}\n"
                content += f"Currency:           {day_data.get('currency') or 'N/A'}\n"
                content += f"Last Dividend:      {self.format_value(day_data.get('last_dividend'))} {day_data.get('currency') or 'in Stock Currency'}\n"
                content += f"Next Ex-Date:       {day_data.get('next_ex_date') or 'N/A'}\n"
                content += f"Frequency:          {day_data.get('frequency') or 'N/A'}\n"
                # Letzte 4 Dividenden
                last_divs = day_data.get('last_dividends', [])
                if last_divs:
                    content += f"\nLast Dividends:\n"
                    for div in last_divs:
                        idx = f"-{div['index']}"
                        date = div['date']
                        percent = f"{div['percent']}%" if div['percent'] is not None else "N/A"
                        content += f"{idx}: {date:<15} {percent}\n"
                content += f"\nLast updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                content = f"No current day data available for {ticker_symbol}"
                
            stock_info = self.db.get_stock_news(ticker_symbol,3)
            if stock_info:
                content += f"\n{'=' * 40}\n\n"
                content += f"Recent News:\n"
                # newest first
                for date, info in stock_info.items():
                    content += f"{date}:\n"
                    content += tools.wrap_text_with_preferred_breaks(info, 80) + "\n\n"

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

    def on_peer_compare_motion(self, event: tk.Event) -> None:
        """
        Zeigt Tooltips mit Spaltenbeschreibung für Peer Compare Treeview.
        """
        region = self.peer_compare_tree.identify("region", event.x, event.y)
        if region != "cell":
            self.peer_compare_tooltip.hidetip()
            return
        col = self.peer_compare_tree.identify_column(event.x)
        col_idx = int(col.replace("#", "")) - 1
        col_names = [
            "SockName", "Spread", "Volume", "Change", "52W Hoch", "Kurs", "52W Tief", "KGV", "Marktkap.", "Health"
        ]
        col_tooltips = {
            "SockName": "Name der Aktie oder des Peer-Unternehmens.",
            "Spread": "Tages-Spread:\nDifferenz zwischen Hoch und Tief als Prozentwert.\nZeigt Volatilität.",
            "Volume": "Handelsvolumen des Tages.\nHohe Werte bedeuten hohe Liquidität.",
            "Change": "Tagesveränderung in Prozent.\nZeigt die Kursbewegung des Tages.",
            "52W Hoch": "Das höchste Kursniveau\nder letzten 52 Wochen.",
            "Kurs": "Aktueller Kurs der Aktie.",
            "52W Tief": "Das niedrigste Kursniveau\nder letzten 52 Wochen.",
            "KGV": "Kurs-Gewinn-Verhältnis\n(trailing/forward PE).\nBewertungskennzahl.",
            "Marktkap.": "Marktkapitalisierung:\nGesamtwert des Unternehmens am Markt.",
            "Health": "Gesundheits-Score:\nBewertet Stabilität,\nBewertung und Liquidität."
        }
        if 0 <= col_idx < len(col_names):
            tip_text = col_tooltips.get(col_names[col_idx], "")
            x = self.peer_compare_tree.winfo_rootx() + event.x + 20
            y = self.peer_compare_tree.winfo_rooty() + event.y + 10
            self.peer_compare_tooltip.showtip(tip_text, x, y)
        else:
            self.peer_compare_tooltip.hidetip()
