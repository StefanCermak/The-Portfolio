import tkinter as tk
import tkinter.ttk as ttk
import sys
import os
import tkinter as tk

import globals
import Db

from Gui_about_tab import AboutTab
from Gui_settings_tab import SettingsTab
from Gui_manual_trade_tab import ManualTradeTab
from Gui_statistics_tab import StatisticsTab
from Gui_trade_history_tab import TradeHistoryTab
from Gui_active_trades_tab import ActiveTradesTab

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

""" GUI for the stock broker application """


class BrokerApp:
    def __new__(cls, *args, **kwargs):
        """Ensures only one instance of BrokerApp is only started once
        This avoids multiple main windows due to pyinstall bug."""
        if not hasattr(cls, '_instance'):
            cls._instance = super(BrokerApp, cls).__new__(cls)
            return cls._instance
        else:
            return None

    def __init__(self):
        """Initialisiert die Hauptanwendung und erstellt alle Tabs und Widgets."""
        self.db = Db.Db()
        self.registered_update_functions = []

        self.Window = tk.Tk()
        self.Window.title(globals.APP_NAME)
        self.tab_control = ttk.Notebook(self.Window)

        self.active_trades_tab = ttk.Frame(self.tab_control)
        self.trade_history_tab = ttk.Frame(self.tab_control)
        self.statistics_tab = ttk.Frame(self.tab_control)
        self.manual_trade_tab = ttk.Frame(self.tab_control)
        self.settings_tab = ttk.Frame(self.tab_control)
        self.about_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.active_trades_tab, text='Active Trades')
        self.tab_control.add(self.trade_history_tab, text='Trade History')
        self.tab_control.add(self.statistics_tab, text='Summary')
        self.tab_control.add(self.manual_trade_tab, text='Manual Trade')
        self.tab_control.add(self.settings_tab, text='Configuration')
        self.tab_control.add(self.about_tab, text='About')
        self.tab_control.pack(expand=1, fill='both')

        # self.setup_tab_active_trades()
        ActiveTradesTab(self.active_trades_tab, self.update_all_tabs, self.register_update_all_tabs)  # <--- NEU
        TradeHistoryTab(self.trade_history_tab, self.register_update_all_tabs)
        StatisticsTab(self.statistics_tab, self.register_update_all_tabs)
        ManualTradeTab(self.manual_trade_tab, self.update_all_tabs, self.register_update_all_tabs)
        SettingsTab(self.settings_tab, self.update_all_tabs, self.register_update_all_tabs)
        AboutTab(self.about_tab)

        # Set application icon, must be done after StatisticsTab (matplotlib)
        if sys.platform.startswith('win'):
            icon_path = os.path.join('graphics', 'The_Portfolio.ico')
            if os.path.exists(icon_path):
                self.Window.iconbitmap(icon_path)
        else: # 'linux' and 'MacOs'
            icon_path = os.path.join('graphics', 'The_Portfolio.png')
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                self.Window.iconphoto(True, img)

        # Initialize auto-update for active trades (every 5 minutes)
        self.auto_update_job = None
        self.start_auto_update()

    def register_update_all_tabs(self, func):
        """Registriert eine Funktion, die aufgerufen wird, wenn alle Tabs aktualisiert werden sollen."""
        self.registered_update_functions.append(func)

    def update_all_tabs(self):
        """Aktualisiert alle Tabs der Anwendung."""
        for update_function in self.registered_update_functions:
            update_function()

    def start_auto_update(self):
        """Startet das automatische Update für aktive Trades alle 5 Minuten."""
        # Schedule the first update
        self.schedule_auto_update()

    def schedule_auto_update(self):
        """Plant das nächste automatische Update ein."""
        # Update every 5 minutes (300,000 milliseconds)
        update_interval = 5 * 60 * 1000  # 5 minutes in milliseconds
        self.auto_update_job = self.Window.after(update_interval, self.perform_auto_update)

    def perform_auto_update(self):
        """Führt das automatische Update der aktiven Trades durch."""
        try:
            # Update the active trades tab
            # self.update_tab_active_trades()
            pass
        except Exception as e:
            print(f"Auto-update failed: {e}")
        finally:
            # Schedule the next update
            self.schedule_auto_update()

    def stop_auto_update(self):
        """Stoppt das automatische Update."""
        if self.auto_update_job is not None:
            self.Window.after_cancel(self.auto_update_job)
            self.auto_update_job = None

    def run(self):
        """Startet die Haupt-Event-Loop der Anwendung."""
        try:
            self.Window.mainloop()
        finally:
            # Clean up auto-update timer when application closes
            self.stop_auto_update()
            globals.save_user_config()
            self.Window.quit()
