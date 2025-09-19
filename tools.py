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

""" 
Utility functions for The Portfolio application, including caching decorators,
path utilities, text wrapping, and tooltip support for tkinter widgets.
"""


# decorators for caching
def timed_cache(ttl_seconds: int = 300):
    """
    Decorator for time-based caching.
    Stores the result of a function for ttl_seconds seconds.

    Args:
        ttl_seconds (int): Lifetime of the cache in seconds.

    Returns:
        Decorated function with caching.
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


def persistent_cache(cache_file: str):
    """
    Decorator for persistent file-based caching.
    Stores function calls and their results in a JSON file.

    Args:
        cache_file (str): Path to the cache file.

    Returns:
        Decorated function with persistent caching.
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


def persistent_timed_cache(cache_file: str, ttl_seconds: int = 86400):
    """
    Dekorator für persistenten, zeitbasierten Cache.
    Speichert Ergebnisse in einer JSON-Datei und prüft die Gültigkeit per TTL.
    """
    def decorator(func):
        # Cache laden
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cache = json.load(f)
            except json.JSONDecodeError:
                cache = {}
        else:
            cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key_raw = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
            key = hashlib.sha256(key_raw.encode()).hexdigest()
            now = time.time()

            # Prüfen, ob Cache gültig ist
            if key in cache:
                entry = cache[key]
                if isinstance(entry, dict) and "timestamp" in entry and "result" in entry:
                    if now - entry["timestamp"] < ttl_seconds:
                        return entry["result"]

            # Neu berechnen und speichern
            result = func(*args, **kwargs)
            cache[key] = {"result": result, "timestamp": now}
            with open(cache_file, "w") as cache_file_ref:
                json.dump(cache, cache_file_ref)
            return result

        return wrapper
    return decorator


def path_smart_shorten(path: str) -> str:
    """
    Shortens a file path for display purposes.
    Replaces the home directory with '~' or uses a relative path if shorter.

    Args:
        path (str): The file path to shorten.

    Returns:
        str: The shortened file path.
    """
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


def wrap_text_with_preferred_breaks(text: str, max_width: int) -> str:
    """
    Wraps the given text to the specified width, preferring line breaks after punctuation.

    Args:
        text (str): The text to wrap.
        max_width (int): The maximum line width.

    Returns:
        str: The wrapped text. Returns an empty string if input text is empty.
    """
    if not text:
        return ""
    lines = []
    line = ""
    for word in text.split():
        if word[-1] in [".", ",", ";", ":", "!", "?"]:
            width = int(max_width * 0.75)
        else:
            width = max_width
        if len(line) + len(word) + 1 > width:
            lines.append(line)
            line = word
        else:
            line += " " + word if line else word
    if line:
        lines.append(line)
    return '\n'.join(lines)


class ToolTip:
    """
    Tooltip widget for tkinter.
    Displays a tooltip with the given text near the associated widget.
    """
    def __init__(self, widget: tk.Widget) -> None:
        """
        Initialize the ToolTip.

        Args:
            widget: The tkinter widget to attach the tooltip to.
        """
        self.widget = widget
        self.tipwindow: tk.Toplevel | None = None
        self.label: tk.Label | None = None

    def showtip(self, text: str, x: int, y: int) -> None:
        """
        Show the tooltip with the given text at the specified (x, y) position.

        Args:
            text (str): The text to display in the tooltip.
            x (int): X-coordinate for the tooltip window.
            y (int): Y-coordinate for the tooltip window.
        """
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

    def hidetip(self) -> None:
        """
        Hide the tooltip if it is currently displayed.
        """
        tw = self.tipwindow
        self.tipwindow = None
        self.label = None
        if tw:
            tw.destroy()
