import tkinter as tk
from tkinter import ttk
import threading
import webbrowser

import RSS_Crawler
import Db


class RssFeedsTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill="both", expand=True)
        self.db = Db.Db()
        self.treeview_id_link_dict = {}

        self.rss_treeview = ttk.Treeview(self.frame, columns=("Server", "Summary"), show='headings')
        self.rss_treeview.heading("Server", text="Server")
        self.rss_treeview.heading("Summary", text="Summary")
        self.rss_treeview.column("Server", width=150)
        self.rss_treeview.column("Summary", width=525)
        self.rss_treeview.pack(fill="both", expand=True)
        self.rss_treeview.insert("", "end", values=("still fetching data", "", "--- please wait ---"))
        self.update_rss_feeds()
        self.rss_treeview.bind("<Double-Button-1>", self.on_treeview_click)

    def update_rss_feeds(self):
        def update_rss_feeds_thread(symbols):
            crawler = RSS_Crawler.RssCrawler()
            crawler.rss_filters = symbols
            server_dict = {}
            for entry in crawler:
                server = entry.server
                if server not in server_dict:
                    server_dict[server] = []
                server_dict[server].append(entry)
                self.rss_treeview.after(0, update_treeview, server_dict, symbols)

        def update_treeview(server_dict, symbols):
            self.rss_treeview.delete(*self.rss_treeview.get_children())
            self.treeview_id_link_dict = {}
            sorted_servers = sorted(server_dict.keys())
            for server in sorted_servers:
                server_line_id = self.rss_treeview.insert("", "end", values=(server, f"-------------------------"))
                entries = server_dict[server]
                for entry in entries:
                    tags = []
                    for tag in symbols:
                        if tag in entry.title.lower() or tag in entry.summary.lower() or (entry.article and tag in entry.article.lower()):
                            tags.append(tag)
                    # sort tags alphabetically, ignore case
                    tags.sort(key=lambda s: s.lower())
                    if tags:
                        tree_id = self.rss_treeview.insert(server_line_id, "end", values=("️🏷" + "️, 🏷".join(tags), entry.title))
                        self.treeview_id_link_dict[tree_id] = entry.link

        stock_names = self.db.get_current_stock_set()
        filter_symbols = []
        for name in stock_names.keys():
            if ' ' in name:
                name = name.split(' ')[0].lower()
            else:
                name = name.lower()

            filter_symbols.append(name)
            ticker = self.db.get_ticker_symbol(name)
            if ticker is None:
                continue
            if '.' in ticker:
                ticker_short = ticker.split('.')[0].lower()
            else:
                ticker_short = ticker.lower()
            filter_symbols.append(ticker_short)

        threading.Thread(target=update_rss_feeds_thread, args=(filter_symbols,), daemon=True).start()

    def on_treeview_click(self, _):
        item_id = self.rss_treeview.focus()
        if not item_id:
            return
        if item_id in self.treeview_id_link_dict:
            link = self.treeview_id_link_dict[item_id]
            webbrowser.open(link)
