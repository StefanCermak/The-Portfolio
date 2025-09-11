import os
import time
import json
import hashlib
from functools import wraps
import tkinter as tk

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

""" Utility functions """


# decorators for caching
def timed_cache(ttl_seconds=300):
    """
    Decorator für zeitbasiertes Caching.
    Speichert das Ergebnis einer Funktion für ttl_seconds Sekunden.

    Args:
        ttl_seconds (int): Lebensdauer des Cache in Sekunden

    Returns:
        Decorated function
    """

    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()

            # Cache vorhanden und gültig?
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result

            # Neu berechnen und speichern
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result

        return wrapper

    return decorator


def persistent_cache(cache_file):
    """
    Decorator für persistenten Datei-Cache.
    Speichert Funktionsaufrufe und deren Ergebnisse in einer JSON-Datei.

    Args:
        cache_file (str): Pfad zur Cache-Datei

    Returns:
        Decorated function
    """
    # Cache laden
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cache = json.load(f)
        except json.JSONDecodeError:
            cache = {}
    else:
        cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Schlüssel generieren (hash bar, auch bei komplexen args)
            key_raw = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
            key = hashlib.sha256(key_raw.encode()).hexdigest()

            if key in cache:
                return cache[key]

            result = func(*args, **kwargs)
            cache[key] = result

            # Cache speichern
            with open(cache_file, "w") as cache_file_ref:
                json.dump(cache, cache_file_ref)

            return result

        return wrapper

    return decorator


def path_smart_shorten(path: str) -> str:
    home_path = os.path.expanduser("~")
    cwd = os.getcwd()

    if path.startswith(home_path):
        tilde_path = path.replace(home_path, "~", 1)
    else:
        tilde_path = path

    try:
        rel_path = os.path.relpath(path, cwd)
    except ValueError:
        rel_path = path  # Falls z. B. Laufwerkswechsel unter Windows

    return rel_path if len(rel_path) < len(tilde_path) else tilde_path


def wrap_text_with_preferred_breaks(text, max_width):
    """Wraps the given text to the specified width."""
    lines = []
    line = ""
    for word in text.split():
        if word[-1] in [".", ",", ";", ":", "!", "?"]:
            width = max_width * 0.75
        else:
            width = max_width
        if len(line) + len(word) + 1 > width:
            lines.append(line)
            line = word
        else:
            line += " " + word
    if line:
        lines.append(line)
    return '\n'.join(lines)

class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.label = None

    def showtip(self, text, x, y):
        if not text:
            return
        if len(text) > 100:
            text = wrap_text_with_preferred_breaks(text, 80)
        if self.tipwindow:
            tw = self.tipwindow
            if self.label:
                self.label.config(text=text)
            tw.wm_geometry(f"+{x}+{y}")
            return

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        self.label = label = tk.Label(tw, text=text, background="#ffffe0", relief="solid", borderwidth=1,
                                      font=("tahoma", 12, "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        self.label = None
        if tw:
            tw.destroy()
