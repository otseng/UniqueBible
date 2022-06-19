import os, sqlite3, config, logging

class IndexSqlite:

    def __init__(self, type, filename, createFile=False):
        if "." not in filename:
            filename += ".index"
        indexDir = os.path.join(config.marvelData, "indexes")
        if not os.path.exists(indexDir):
            os.mkdir(indexDir)
        indexDir = os.path.join(indexDir, type)
        if not os.path.exists(indexDir):
            os.mkdir(indexDir)
        filePath = os.path.join(indexDir, filename)
        if not os.path.exists(filePath) and not createFile:
            raise Exception(f"Could not open {filePath}")

        self.type = type
        self.filename = filename
        self.connection = sqlite3.connect(filePath)
        self.cursor = self.connection.cursor()
        self.logger = logging.getLogger('uba')
        if not self.checkTableExists():
            self.createTable()

    def __del__(self):
        self.connection.close()

    def createTable(self):
        if self.type == "bible":
            sql = "CREATE TABLE IF NOT EXISTS Index_Data (Word NVARCHAR(50), Book INT, Chapter INT, Verse INT)"
            self.cursor.execute(sql)

    def checkTableExists(self):
        if self.type == "bible":
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='Index_Data'")
            if self.cursor.fetchone():
                return True
        return False

    def insertBibleData(self, content):
        insert = "INSERT INTO Index_Data (Word, Book, Chapter, Verse) VALUES (?, ?, ?, ?)"
        self.cursor.executemany(insert, content)
        self.connection.commit()

    def deleteAll(self):
        delete = "DELETE FROM Index_Data"
        self.cursor.execute(delete)
        self.connection.commit()

