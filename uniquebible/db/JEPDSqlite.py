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
        print(f"Inserting {b},{c},{v},{start},{end},{source}")
        # insert = "INSERT INTO Mapping (Book, Chapter, Verse, Start, End, Source) VALUES (?, ?, ?, ?, ?, ?)"
        # self.cursor.execute(insert, (b, c, v, start, end, source))

    def processLine(self, book, line, source):
        start = ''
        end = ''
        print(f">>>>> {line}")
        if "-" not in line:
            # 31:49
            values = line.split(":")
            chapter = int(values[0])
            verse = int(values[1])
            self.insertMapping(book, chapter, verse, start, end, source)
        else:
            values = line.split("-")
            passageStart = values[0]
            verseEnd = values[1]
            if ":" not in verseEnd:
                # 50:1-11
                values = passageStart.split(":")
                chapter = int(values[0])
                verseStart = values[1]
                for verse in range(int(verseStart), int(verseEnd)+1):
                    self.insertMapping(book, chapter, verse, start, end, source)
            else:
                try:
                    values = line.split("-")
                    passageStart = values[0]
                    passageEnd = values[1]
                    values = passageStart.split(":")
                    chapterStart = int(values[0])
                    values = values[1].split(".")
                    verseStart = int(values[0])
                    chunkStart = int(values[1])
                    values = passageEnd.split(":")
                    values = values[1].split(".")
                    verseEnd = int(values[0])
                    chunkEnd = int(values[1])
                    if verseStart == verseEnd:
                        # 21:1.1-21:1.6
                        # 46:5.5-46:5.99
                        self.insertMapping(book, chapterStart, verseStart, chunkStart, chunkEnd, source)
                    else:
                        # 12:1.1-12:4.9
                        # 2:4.6 - 2:25.99
                        if chunkStart == 1:
                            self.insertMapping(book, chapterStart, verseStart, '', '', source)
                        else:
                            self.insertMapping(book, chapterStart, verseStart, chunkStart, 99, source)
                        for verse in range(verseStart+1, verseEnd):
                            self.insertMapping(book, chapterStart, verse, '', '', source)
                        if chunkEnd == 99:
                            self.insertMapping(book, chapterStart, verseEnd, '', '', source)
                        else:
                            self.insertMapping(book, chapterStart, verseEnd, 1, chunkEnd, source)
                except:
                    print("!!!!!!!!!!!")
                    print(f"Cannot process {line}")


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

