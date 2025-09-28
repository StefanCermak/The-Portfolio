import tkinter as tk
from tkinter import ttk
import threading
import webbrowser
import re

import RSS_Crawler
import Db
import tools


GET_FILTER_RE = re.compile(r'(?<!\w){}(?!\w)')


class RssFeedsTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill="both", expand=True)
        self.db = Db.Db()
        self.treeview_id_additional_datas = {}

        self.rss_treeview = ttk.Treeview(self.frame, columns=("Server", "Summary"), show='tree headings')
        self.rss_treeview.heading("Server", text="Server")
        self.rss_treeview.heading("Summary", text="Summary")
        self.rss_treeview.column("#0", width=30, stretch=False)
        self.rss_treeview.column("Server", width=200, stretch=False)
        self.rss_treeview.column("Summary", width=600)
        self.rss_treeview.pack(fill="both", expand=True)
        self.rss_treeview.insert("", "end", values=("still fetching data", "", "--- please wait ---"))
        self.update_rss_feeds()
        self.rss_treeview.bind("<Double-Button-1>", self.on_treeview_click)
        self.rss_treeview.bind("<Motion>", self.on_treeview_motion)
        self.rss_treeview.bind("<Leave>", lambda e: self.tooltip.hidetip())

        self.tooltip = tools.ToolTip(self.rss_treeview)

    def update_rss_feeds(self):
        def update_rss_feeds_thread(symbols):
            crawler = RSS_Crawler.RssCrawler()
            server_dict = {}
            for entry in crawler.filtered_entries(symbols):
                server = entry.server
                if server not in server_dict:
                    server_dict[server] = []
                server_dict[server].append(entry)
                self.rss_treeview.after(0, update_treeview, server_dict, symbols)

        def update_treeview(server_dict, symbols):
            self.rss_treeview.delete(*self.rss_treeview.get_children())
            self.treeview_id_additional_datas = {}
            sorted_servers = sorted(server_dict.keys())
            for server in sorted_servers:
                spaltenbreite = self.rss_treeview.column("Summary", option="width")
                zeichen_pro_pixel = 0.7  # ggf. anpassen
                anzahl_zeichen = int(spaltenbreite * zeichen_pro_pixel)
                trennstrich = "─" * anzahl_zeichen
                server_line_id = self.rss_treeview.insert("", "end", values=(server, trennstrich))
                entries = server_dict[server]
                for entry in entries:
                    filter_collection = (
                        (entry.title.lower() + " ") +
                        (entry.summary.lower() if entry.summary else "") + " " +
                        (entry.article.lower() if entry.article else ""))
                    tags = []
                    for tag in symbols:
                        if re.search(GET_FILTER_RE.pattern.format(re.escape(tag)), filter_collection):
                            tags.append(tag)
                    # sort tags alphabetically, ignore case
                    tags.sort(key=lambda s: s.lower())
                    if tags:
                        tree_id = self.rss_treeview.insert(server_line_id, "end", values=("️", entry.title))
                        self.treeview_id_additional_datas[tree_id] = {'link': entry.link, 'hint': "️🏷" + "️, 🏷".join(tags)}
            # expand all servers
            for server in sorted_servers:
                server_line_id = self.rss_treeview.get_children()[sorted_servers.index(server)]
                self.rss_treeview.item(server_line_id, open=True)

        stock_names = self.db.get_current_stock_set()
        filter_symbols = []
        for name in stock_names.keys():
            ticker = self.db.get_ticker_symbol(name)
            if ' ' in name:
                name = name.split(' ')[0].lower()
            else:
                name = name.lower()

            filter_symbols.append(name)
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
        if item_id in self.treeview_id_additional_datas:
            link = self.treeview_id_additional_datas[item_id]['link']
            webbrowser.open(link)

    def on_treeview_motion(self, event):
        item_id = self.rss_treeview.identify_row(event.y)
        if not item_id:
            self.tooltip.hidetip()
            return
        if item_id in self.treeview_id_additional_datas:
            hint = self.treeview_id_additional_datas[item_id]['hint']
            x = event.x_root + 20
            y = event.y_root + 10
            self.tooltip.showtip(hint, x, y)
        else:
            self.tooltip.hidetip()
