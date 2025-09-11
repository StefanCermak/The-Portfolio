import tkinter as tk
from tkinter import ttk, filedialog

import globals
import tools
import Db


class SettingsTab:
    def __init__(self, parent, update_all_tabs_callback, register_update_all_tabs):
        """Initialisiert das Settings-Tab mit allen Konfigurationsoptionen."""
        self.db = Db.Db()
        self.update_all_tabs = update_all_tabs_callback
        register_update_all_tabs(self.update_tab_settings)

        self.frame_ticker_matching = ttk.LabelFrame(parent,
                                                    text="Ticker Symbol <-> Personal Stock Name Matching")
        self.frame_ticker_matching.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")
        self.label_ticker_matching = ttk.Label(self.frame_ticker_matching,
                                               text="Select the Stock Name to be shown instead of the Ticker Symbol")
        self.label_ticker_matching.grid(column=0, row=0, padx=10, pady=10, columnspan=4)

        self.setup_combobox_stockname_symbol_matching = ttk.Combobox(self.frame_ticker_matching,
                                                                     values=[], state="readonly")
        self.setup_combobox_stockname_symbol_matching.grid(column=0, row=1, padx=10, pady=10)

        self.setup_combobox_stockname_ticker_matching = ttk.Combobox(self.frame_ticker_matching,
                                                                     values=[],
                                                                     state="readonly")
        self.setup_combobox_stockname_ticker_matching.grid(column=1, row=1, padx=10, pady=10)

        self.setup_edit_stockname_new_symbol = ttk.Entry(self.frame_ticker_matching, width=20)
        self.setup_edit_stockname_new_symbol.grid(column=2, row=1, padx=10, pady=10)

        self.button_store_long_name = ttk.Button(self.frame_ticker_matching, text="Store Long Name",
                                                 command=self.store_long_name)
        self.button_store_long_name.grid(column=3, row=1, padx=10, pady=10)

        self.setup_combobox_stockname_ticker_matching.bind("<<ComboboxSelected>>",
                                                           self.on_setup_combobox_stockname_ticker_matching_selected)
        self.setup_combobox_stockname_symbol_matching.bind("<<ComboboxSelected>>",
                                                           self.on_setup_combobox_stockname_symbol_matching_selected)

        self.frame_import_account_statements = ttk.LabelFrame(parent, text="Import Account Statements")
        self.frame_import_account_statements.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
        self.label_import_account_statements_folder = ttk.Label(self.frame_import_account_statements,
                                                                text="Import account statements from PDF files in a folder:")
        self.label_import_account_statements_folder.grid(column=0, row=0, padx=10, pady=10)
        self.strvar_import_account_statements_folder_path = tk.StringVar()
        self.entry_import_account_statements_folder_path = ttk.Entry(self.frame_import_account_statements,
                                                                     textvariable=self.strvar_import_account_statements_folder_path,
                                                                     width=50)
        self.entry_import_account_statements_folder_path.grid(column=1, row=0, padx=10, pady=10)
        self.button_browse_import_account_statements_folder = ttk.Button(self.frame_import_account_statements,
                                                                         text="Browse",
                                                                         command=self.browse_import_account_statements_folder)
        self.button_browse_import_account_statements_folder.grid(column=2, row=0, padx=10, pady=10)
        self.button_import_account_statements = ttk.Button(self.frame_import_account_statements,
                                                           text="Import Account Statements",
                                                           command=self.import_account_statements)
        self.button_import_account_statements.grid(column=0, row=1, columnspan=3, padx=10, pady=10)
        if "account_statements_folder" in globals.USER_CONFIG and globals.USER_CONFIG[
            "account_statements_folder"] != "":
            self.strvar_import_account_statements_folder_path.set(globals.USER_CONFIG["account_statements_folder"])

        self.frame_ai_configuration = ttk.LabelFrame(parent, text="AI Configuration")
        self.frame_ai_configuration.grid(column=0, row=2, padx=10, pady=10, sticky="nsew")
        self.label_openai_api_key = ttk.Label(self.frame_ai_configuration, text="OpenAI API Key:")
        self.label_openai_api_key.grid(column=0, row=0, padx=10, pady=10)
        self.entry_openai_api_key = ttk.Entry(self.frame_ai_configuration, width=50)
        self.entry_openai_api_key.grid(column=1, row=0, padx=10, pady=10)
        if "OPEN_AI_API_KEY" in globals.USER_CONFIG and globals.USER_CONFIG["OPEN_AI_API_KEY"] != "":
            self.entry_openai_api_key.insert(0, globals.USER_CONFIG["OPEN_AI_API_KEY"])
        self.button_strore_openai_api_key = ttk.Button(self.frame_ai_configuration, text="Store API Key",
                                                       command=self.store_openai_api_key)
        self.button_strore_openai_api_key.grid(column=2, row=0, padx=10, pady=10)
        self.label_openai_api_key_info = ttk.Label(self.frame_ai_configuration,
                                                   text="You can get an API key from https://platform.openai.com/account/api-keys")
        self.label_openai_api_key_info.grid(column=0, row=1, columnspan=2, padx=10, pady=10)
        self.button_openai_website = ttk.Button(self.frame_ai_configuration, text="Open OpenAI Website",
                                                command=lambda: tools.webbrowser.open(
                                                    "https://platform.openai.com/account/api-keys"))
        self.button_openai_website.grid(column=3, row=1, padx=10, pady=10)

        # Initiales Update
        self.update_tab_settings()

    def update_tab_settings(self):

        """Aktualisiert die Inhalte des Settings-Tabs, z.B. Combobox-Werte und Felder."""
        # Beispielhafte Logik, bitte ggf. anpassen/ergänzen:
        # Stockname <-> Ticker Comboboxen aktualisieren
        stocknames_with_tickers = self.db.get_stocknames_with_tickers()
        self.setup_combobox_stockname_symbol_matching['values'] = sorted(stocknames_with_tickers.values())
        self.setup_combobox_stockname_ticker_matching['values'] = sorted(stocknames_with_tickers.keys())

    def store_long_name(self):
        """Speichert einen neuen langen Namen für ein Ticker-Symbol."""
        ticker_symbol = self.setup_combobox_stockname_ticker_matching.get()
        stockname = self.setup_edit_stockname_new_symbol.get()
        if ticker_symbol == "" or stockname == "":
            return
        self.db.add_stockname_ticker(stockname, ticker_symbol, True)
        self.update_all_tabs()
        self.setup_combobox_stockname_symbol_matching.set(stockname)

    def on_setup_combobox_stockname_ticker_matching_selected(self, _):
        """Aktualisiert die Anzeige, wenn ein Ticker im Matching-Tab ausgewählt wird."""
        ticker_symbol = self.setup_combobox_stockname_ticker_matching.get()
        stockname = self.db.get_stockname(ticker_symbol)
        if stockname is not None:
            self.setup_combobox_stockname_symbol_matching.set(stockname)
            self.setup_edit_stockname_new_symbol.delete(0, tk.END)
            self.setup_edit_stockname_new_symbol.insert(0, stockname)

    def on_setup_combobox_stockname_symbol_matching_selected(self, _):
        """Aktualisiert die Anzeige, wenn ein Aktienname im Matching-Tab ausgewählt wird."""
        stockname = self.setup_combobox_stockname_symbol_matching.get()
        ticker_symbol = self.db.get_ticker_symbol(stockname)
        if ticker_symbol is not None:
            self.setup_combobox_stockname_ticker_matching.set(ticker_symbol)
            self.setup_edit_stockname_new_symbol.delete(0, tk.END)
            self.setup_edit_stockname_new_symbol.insert(0, stockname)

            def browse_import_account_statements_folder(self):
                """Öffnet einen Dialog zur Auswahl eines Ordners für Kontoauszüge."""
                folder_path = filedialog.askdirectory(
                    initialdir=self.strvar_import_account_statements_folder_path.get())
                if folder_path:
                    folder_path = tools.path_smart_shorten(folder_path)
                    self.strvar_import_account_statements_folder_path.set(folder_path)
                    globals.USER_CONFIG["account_statements_folder"] = folder_path
                    globals.save_user_config()

                    def browse_import_account_statements_folder(self):
                        """Öffnet einen Dialog zur Auswahl eines Ordners für Kontoauszüge."""
                        folder_path = filedialog.askdirectory(
                            initialdir=self.strvar_import_account_statements_folder_path.get())
                        if folder_path:
                            folder_path = tools.path_smart_shorten(folder_path)
                            self.strvar_import_account_statements_folder_path.set(folder_path)
                            globals.USER_CONFIG["account_statements_folder"] = folder_path
                            globals.save_user_config()

    def browse_import_account_statements_folder(self):
        """Öffnet einen Dialog zur Auswahl eines Ordners für Kontoauszüge."""
        folder_path = filedialog.askdirectory(initialdir=self.strvar_import_account_statements_folder_path.get())
        if folder_path:
            folder_path = tools.path_smart_shorten(folder_path)
            self.strvar_import_account_statements_folder_path.set(folder_path)
            globals.USER_CONFIG["account_statements_folder"] = folder_path
            globals.save_user_config()

    def import_account_statements(self):
        """Importiert Kontoauszüge aus dem ausgewählten Ordner."""
        folder_path = self.strvar_import_account_statements_folder_path.get()
        if folder_path:
            import_account_statements.from_folder(folder_path, self.db)
            self.update_all_tabs()

    def store_openai_api_key(self):
        """Speichert den OpenAI API Key in der Konfiguration."""
        api_key = self.entry_openai_api_key.get().strip()
        globals.USER_CONFIG["OPEN_AI_API_KEY"] = api_key
        globals.save_user_config()