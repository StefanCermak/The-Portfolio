import json
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


""" Global constants and configuration management for the portfolio application. """
# app info

APP_VERSION = "release-0.5.0"
APP_NAME = "The Portfolio"
APP_AUTHOR = "Stefan Cermak"
APP_DESCRIPTION = "A simple portfolio management application."
APP_COPYRIGHT = " This Project is developed unter the GPLv3."

# files
CONFIG_FILE = "config.json"
SQLITE_FILE = "portfolio.db"
LOG_FILE = "portfolio.log"

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMEZONE = "Europe/Vienna"
CURRENCY = "EUR"
PROFIT_THRESHOLD = 0.005

def load_user_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            "USE_SQLITE": True,
            "USE_MARIADB": False,  # one of USE_SQLITE or USE_MARIADB must be True
                                   # if both are True, Mariadb is used as primary storage,
                                   # sqlite will stay in sync, and if offline,
                                   # sqlite is used in read-only mode for viewing data

            "MARIADB_HOST": "localhost",
            "MARIADB_PORT": 3306,
            "MARIADB_USER": "guest",
            "MARIADB_PASSWORD": "guest",
            "MARIADB_DB": "portfolio",

            "OPEN_AI_API_KEY": "",
        }


def save_user_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(USER_CONFIG, f, indent=4)


USER_CONFIG = load_user_config()
