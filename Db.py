
import globals
import Db_Sqlite


class Db:
    def __init__(self):
        if globals.USER_CONFIG["USE_SQLITE"]:
            self.db_sqlite = Db_Sqlite.DbSqlite()
        else:
            self.db_sqlite = None

    def close(self):
        if self.db_sqlite is not None:
            self.db_sqlite.close()
            self.db_sqlite = None
