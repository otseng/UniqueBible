import os, apsw
import re

import config
from util.BibleBooks import BibleBooks


class StatisticsSqlite:

    FILE_DIRECTORY = "statistics"
    FILE_NAME = "words.sqlite"
    TABLE_NAME = "data"
    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {0} (Strongs NVARCHAR(6), Original NVARCHAR(50), Transliteration NVARCHAR(50), Frequency INT)".format(TABLE_NAME)

    def __init__(self):
        indexDir = os.path.join(config.marvelData, self.FILE_DIRECTORY)
        if not os.path.exists(indexDir):
            os.mkdir(indexDir)
        self.filename = os.path.join(config.marvelData, self.FILE_DIRECTORY, self.FILE_NAME)
        self.connection = apsw.Connection(self.filename)
        self.cursor = self.connection.cursor()
        if not self.checkTableExists():
            self.createTable()

    def close(self):
        self.connection.close()

    def createTable(self):
        self.cursor.execute(self.CREATE_TABLE)

    def checkTableExists(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}'".format(self.TABLE_NAME))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def insert(self, strongs, original, transliteration, frequency):
        if not self.checkStrongsExists(strongs):
            insert = "INSERT INTO {0} (Strongs, Original, Transliteration, Frequency) VALUES (?, ?, ?, ?)".format(self.TABLE_NAME)
            self.cursor.execute(insert, (strongs, original, transliteration, frequency))

    def delete(self, strongs):
        delete = "DELETE FROM {0} WHERE Strongs=?".format(self.TABLE_NAME)
        self.cursor.execute(delete, (strongs,))

    def deleteAll(self):
        delete = "DELETE FROM {0}".format(self.TABLE_NAME)
        self.cursor.execute(delete)

    def deleteHebrew(self):
        delete = "DELETE FROM {0} WHERE Strongs like 'H%'".format(self.TABLE_NAME)
        self.cursor.execute(delete)

    def checkStrongsExists(self, Strongs):
        query = "SELECT * FROM {0} WHERE Strongs=?".format(self.TABLE_NAME)
        self.cursor.execute(query, (Strongs,))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def getFrequency(self, strongs):
        query = "SELECT Frequency FROM {0} WHERE Strongs=?".format(self.TABLE_NAME)
        self.cursor.execute(query, (strongs,))
        data = self.cursor.fetchone()
        if data:
            return int(str(data[0]).replace(",", ""))
        else:
            return 0

    def getAllStrongsFrequency(self):
        query = "SELECT Strongs, Frequency FROM {0} ORDER BY Strongs".format(self.TABLE_NAME)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def getAll(self):
        query = "SELECT * FROM {0} ORDER BY Strongs".format(self.TABLE_NAME)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @staticmethod
    def testCreate():
        db = StatisticsSqlite()
        db.deleteAll()
        db.insert("G2424", "Ἰησοῦς", "Iēsous", "975")

    @staticmethod
    def listAll():
        db = StatisticsSqlite()
        records = db.getAll()
        for record in records:
            print("{0}:{1}:{2}:{3}".format(record[0], record[1], record[2], record[3]))


    # Almost 15,000 unique Strongs words
    # 5,624 Greek
    # 8,674 Hebrew
    # https://en.wikipedia.org/wiki/Strong%27s_Concordance
    @staticmethod
    def populateDatabase():

        from db.ToolsSqlite import Lexicon

        db = StatisticsSqlite()
        db.deleteHebrew()

        lexicon = Lexicon('TRLIT')
        topics = lexicon.getHebrewTopics()
        print("Processing " + str(len(topics)))
        max_records = 15000
        count = 0
        for data in topics:
            strongs = data[0]
            entry = lexicon.getRawContent(strongs)[0]
            if "Transliteration" in entry and "Occurs" in entry:
                entry = entry.replace("\n", " ")
                if count % 1000 == 0:
                    print(count)
                try:
                    search = re.search(r"<grk>(.*?)</grk>.*Transliteration: .*?>(.*?)<\/a>.*?Occurs (.*?) ", entry)
                    (original, transliteration, frequency) = search.groups()
                    # print("{0}:{1}".format(transliteration, frequency))
                except:
                    print("Error in " + strongs)
                if not db.checkStrongsExists(strongs):
                    db.insert(strongs, original.strip(), transliteration, frequency)

            count += 1
            if count > max_records:
                break

    @staticmethod
    def testReplace():
        db = StatisticsSqlite()

        text = "The book G976 of the generation G1078 of Jesus G2424 Christ G5547 , the son G5207 of David G1138 , the son G5207 of Abraham G11 ."

        matches = re.findall(r" ([GH][0-9]*?) ", text)

        highlightMapping = [(0, 0, "gray"),
                            (1, 1, "red"),
                            (2, 100, "blue"),
                            (101, 500, "green"),
                            (501, 10000, "orange")]
        for strongs in set(matches):
            frequency = db.getFrequency(strongs)
            color = ""
            for map in highlightMapping:
                if frequency >= map[0] and frequency <= map[1]:
                    color = map[2]
            if color:
                text = StatisticsSqlite.addHighlightTagToPreviousWord(text, strongs, color, frequency)
        print(text)

    @staticmethod
    def addHighlightTagToPreviousWord(text, searchWord, color, frequency):
        searchWord = " " + searchWord + " "
        startSearch = 0
        while searchWord in text[startSearch:]:
            end_ptr = text.find(searchWord, startSearch)
            start_ptr = end_ptr - 1
            while text[start_ptr] != " ":
                start_ptr = start_ptr - 1
                if start_ptr == 0:
                    break
            if start_ptr > 0:
                start_ptr =start_ptr + 1
            replaceWord = text[start_ptr:end_ptr].strip()
            replace = '<span color="' + color + '">' + replaceWord + '<sub>' + str(frequency) + '</sub></span>'
            text = text[:start_ptr] + replace + text[end_ptr:]
            startSearch = end_ptr + len(replace)
        return text

    @staticmethod
    def findMissingLexicons():
        from db.BiblesSqlite import BiblesSqlite

        db = StatisticsSqlite()
        biblesSqlite = BiblesSqlite()
        missingStrongs = set()

        for book in range(13, 16):
            print(book)
            chapters = BibleBooks.chapters[book]
            for chapter in range(1, chapters):
                contents = biblesSqlite.readTextChapter("KJVx", book, chapter)
                for line in contents:
                    text = line[3]
                    matches = re.findall(r" ([GH][0-9]*?) ", text)
                    for strongs in set(matches):
                        frequency = db.getFrequency(strongs)
                        if frequency == 0:
                            missingStrongs.add(strongs)
        for strongs in missingStrongs:
            print("./cs.sh " + strongs)


if __name__ == "__main__":

    config.noQt = True
    config.mainB = ''
    config.mainC = ''
    config.mainV = ''
    config.mainText = ''
    config.commentaryB = ''
    config.commentaryC = ''
    config.commentaryV = ''
    config.commentaryText = ''

    config.marvelData = "/home/oliver/dev/UniqueBible/marvelData/"

    # StatisticsSqlite.testCreate()
    # StatisticsSqlite.listAll()

    StatisticsSqlite.testReplace()

    # StatisticsSqlite.populateDatabase()

    # StatisticsSqlite.findMissingLexicons()



