import os
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

def path_smart_shorten(path:str) -> str:
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