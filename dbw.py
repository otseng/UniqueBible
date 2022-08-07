import config

class Connection:

    def __new__(self, database):
        if config.enableBinaryRunMode:
            import sqlite3
            return sqlite3.Connection(database)
        else:
            import apsw
            return apsw.Connection(database)

