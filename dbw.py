import config
import apsw
import sqlite3

class Connection:

    def __new__(self, database):
        if config.enableBinaryRunMode:
            return sqlite3.Connection(database)
        else:
            return apsw.Connection(database)

