import os, sqlite3, config, logging

class IndexSqlite:

    def __init__(self, type, filename, createFile=False):
        self.exists = False

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
            return

        self.type = type
        self.filename = filename
        self.connection = sqlite3.connect(filePath)
        self.cursor = self.connection.cursor()
        self.logger = logging.getLogger('uba')
        if not self.checkTableExists():
            if not createFile:
                return
            else:
                self.createTable()

        self.exists = True

    def __del__(self):
        if self.exists:
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

    def getVerses(self, word):
        sql = "SELECT Book, Chapter, Verse FROM Index_Data WHERE Word=? ORDER BY Book, Chapter, Verse"
        self.cursor.execute(sql, (word,))
        data = self.cursor.fetchall()
        return data

    def deleteAll(self):
        delete = "DELETE FROM Index_Data"
        self.cursor.execute(delete)
        self.connection.commit()

    def deleteBook(self, book):
        delete = "DELETE FROM Index_Data WHERE Book=?"
        self.cursor.execute(delete, (book,))
        self.connection.commit()

