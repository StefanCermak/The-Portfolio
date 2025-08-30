import json
import os

APP_VERSION = "0.0.1"
APP_NAME = "The Portfolio"
APP_AUTHOR = "Stefan Cermak"
APP_DESCRIPTION = "A simple portfolio management application."
APP_COPYRIGHT = "2025 Stefan Cermak"

# files
CONFIG_FILE = "config.json"
SQLITE_FILE = "portfolio.db"
LOG_FILE = "portfolio.log"

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMEZONE = "Europe/Vienna"
CURRENCY = "EUR"


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
        }


def save_user_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(USER_CONFIG, f, indent=4)


USER_CONFIG = load_user_config()
