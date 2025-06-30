import os, apsw, re
from uniquebible import config
from uniquebible.util.BibleVerseParser import BibleVerseParser
import JEPDData

class JEPDSqlite:

    CREATE_MAPPING_TABLE = "CREATE TABLE IF NOT EXISTS Mapping (Book INT, Chapter INT, Verse INT, Start INT, End INT, Source NVARCHAR(5))"

    def __init__(self):
        self.filename = os.path.join(config.marvelData, "JEPD.sqlite")
        self.connection = apsw.Connection(self.filename)
        self.cursor = self.connection.cursor()
        if not self.checkTableExists("Mapping"):
            self.createMappingTable()

    def __del__(self):
        try:
            self.connection.close()
        except:
            pass

    def createMappingTable(self):
        self.cursor.execute(JEPDSqlite.CREATE_MAPPING_TABLE)

    def checkTableExists(self, tablename):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tablename}'")
        if self.cursor.fetchone():
            return True
        else:
            return False

    def deleteAll(self):
        delete = "DELETE FROM Mapping"
        self.cursor.execute(delete)

    def insertMapping(self, b, c, v, start, end, source):
        print(f"Inserting {b}, {c}, {v}, {start}, {end}, {source}")
        # insert = "INSERT INTO Mapping (Book, Chapter, Verse, Start, End, Source) VALUES (?, ?, ?, ?, ?, ?)"
        # self.cursor.execute(insert, (b, c, v, start, end, source))

    def processLine(self, book, line, source):
        chapter = ''
        verse = ''
        start = ''
        end = ''
        print(f">>> {line}")
        if "-" not in line:
            values = line.split(":")
            chapter = values[0]
            verse = values[1]
            # self.insertMapping(book, chapter, verse, start, end, source)
        else:
            values = line.split("-")
            passageStart = values[0]
            passageEnd = values[1]
            if ":" not in passageEnd:
                values = passageStart.split(":")
                chapter = values[0]
                verse = values[1]
                print(line)
                print(f"{book} {chapter} {verse} {start} {end} {source}")

    def loadData(self):
        data = JEPDData.jepd

        for book, bookData in data.items():
            for source, info in bookData.items():
                lines = info.splitlines()
                for line in lines:
                    line = line.replace(",", "").strip()
                    if (line):
                        if line[-1] == ".":
                            line = line[0:-1]
                        self.processLine(book, line, source)

if __name__ == "__main__":
    jepd = JEPDSqlite()
    jepd.deleteAll()
    jepd.loadData()

