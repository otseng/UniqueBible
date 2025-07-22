import sqlite3, re, platform
from uniquebible.db.JEPDSqlite import JEPDSqlite
from uniquebible.util.AGBsubheadings import agbSubheadings
from uniquebible.util.BibleBooks import BibleBooks


class JEPDUtil:

    def __init__(self):
        self.home = '/Users/otseng'
        if platform.system() == "Linux":
            self.home = '/home/oliver'
        self.KJVx = self.home + '/UniqueBible/marvelData/bibles/KJVx.bible'
        self.connectionKJVx = sqlite3.connect(self.KJVx)
        self.cursorKJVx = self.connectionKJVx.cursor()
        self.JEPD_KJV_BIBLE = self.home + '/UniqueBible/marvelData/bibles/JEPD.bible'
        self.connectionJEPDKJV = sqlite3.connect(self.JEPD_KJV_BIBLE)
        self.cursorJEPDKJV = self.connectionJEPDKJV.cursor()
        self.MOB_BIBLE = self.home + '/UniqueBible/marvelData/bibles/MOB.bible'
        self.connectionMOB = sqlite3.connect(self.MOB_BIBLE)
        self.cursorMOB = self.connectionMOB.cursor()

        self.JPEDSqlite = JEPDSqlite()

    def __del__(self):
        self.connectionKJVx.close()
        self.connectionJEPDKJV.commit()
        self.connectionJEPDKJV.close()

    def read_verse(self, book_num, chapter_num, verse_num, bible):
        sql = 'SELECT * from Verses where Book=' + str(book_num) \
               + ' and Chapter=' + str(chapter_num) + ' and Verse=' + str(verse_num)
        if bible == "KJV":
            self.cursorKJVx.execute(sql)
            data = self.cursorKJVx.fetchone()
            return data[3]
        else:
            print(f"!!! Unknown {bible}")

    def read_mob_verse(self, book_num, chapter_num, verse_num):
        sql = 'SELECT * from Verses where Book=' + str(book_num) \
               + ' and Chapter=' + str(chapter_num) + ' and Verse=' + str(verse_num)
        self.cursorMOB.execute(sql)
        data = self.cursorMOB.fetchone()
        return data[3]

    def get_mob_word_count(self, book_num, chapter_num, verse_num):
        data = self.read_mob_verse(book_num, chapter_num, verse_num)
        data = data.replace("<heb>", "").replace("</heb>", "").strip()
        return len(data.split())

    def find_marker(self, word_position, total_words, passage):
        start = int(len(passage) * (word_position / total_words))
        for offset in range(1, 100):
            if (start - offset) > 0 and self.is_punctuation(passage[start - offset]):
                return start - offset
            if (start + offset) < len(passage) and self.is_punctuation(passage[start + offset]):
                return start + offset
        print(f"!!!! could not find punctuation for {start} : {word_position} : {total_words} - {passage}")

    def is_punctuation(self, ch):
        return ch in ",.;:"

    def split_verse(self, start, end, passage, word_count):
        start_position = 0
        end_position = len(passage)
        if start > 1:
            start_position = self.find_marker(start-1, word_count, passage) + 1
        if end < 99:
            end_position = self.find_marker(end, word_count, passage)
        passage = passage[start_position:end_position+1]
        # print(f"{start}, {end}, {word_count}, {passage}")
        return passage

    def create_bible_mapping(self, bible):
        count = 0
        for b in range(1, 6):
            book = BibleBooks.abbrev["eng"][str(b)][1]
            chapters = BibleBooks.chapters[b]
            for c in range(1, chapters+1):
                print(f"Processing {book}: {c}")
                verses = BibleBooks.verses[b][c]
                for v in range(1, verses+1):
                    mappings = self.JPEDSqlite.getMapping(b, c, v)
                    for mapping in mappings:
                        start = mapping[3]
                        end = mapping[4]
                        source = mapping[5]
                        passage = self.read_verse(b, c, v, bible)
                        if not start:
                            jepd.JPEDSqlite.insertVerse(b, c, v, '', '', source, bible, passage)
                        else:
                            start = int(start)
                            end = int(end)
                            word_count = self.get_mob_word_count(b, c, v)
                            passage = self.split_verse(start, end, passage, word_count)
                            jepd.JPEDSqlite.insertVerse(b, c, v, start, end, source, bible, passage)

    def create_bible_tables(self, cursor):
        cursor.execute('DROP TABLE IF EXISTS Bible;')
        cursor.execute('DROP TABLE IF EXISTS Details;')
        cursor.execute('DROP TABLE IF EXISTS Verses;')
        cursor.execute('DROP TABLE IF EXISTS Notes;')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Details (Title NVARCHAR(100), 
                               Abbreviation NVARCHAR(50), Information TEXT, Version INT, OldTestament BOOL,
                               NewTestament BOOL, Apocrypha BOOL, Strongs BOOL);
                            ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Bible (Book INT, Chapter INT, Scripture TEXT);
                            ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Verses (Book INT, Chapter INT, Verse INT, Scripture TEXT);
                            ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Notes (Book INT, Chapter INT, Verse INT, ID TEXT, Note TEXT);
                            ''')
        sql = ("INSERT INTO Details VALUES ('JEPD Bible with sources', 'JEPD',"
               "'JEPD Coded KJV text of Pentateuch.  Based on https://tanach.us/', 1, 1, 0, 0, 1);")
        cursor.execute(sql)

    def delete_strongs(self, line):
        res = line
        res = re.sub(" H\d{1,4}", " ", res)
        res = res.replace("  ", " ")
        res = res.replace(" .", ".")
        res = res.replace(" ;", ";")
        res = res.replace(" :", ":")
        res = res.replace(" ,", ",")
        return res

    def insert_verse(self, cursor, book_num, chapter_num, verse_num, text):
        text = text.replace("'", "''")
        text = text.replace('"', '\"')
        # print("Inserting book {0} chapter {1} verse {2} - {3}".format(book_num, chapter_num, verse_num, text))
        sql = ("INSERT INTO Verses VALUES ({0}, {1}, {2}, '{3}');".format(book_num, chapter_num, verse_num, text))
        cursor.execute(sql)

    def insert_chapter(self, cursor, book_num, chapter_num, text):
        text = text.replace("'", "''")
        text = text.replace('"', '\"')
        text = text.replace('\n', '')
        # print("Inserting book {0} chapter {1}".format(book_num, chapter_num))
        sql = ("INSERT INTO Bible (Book, Chapter, Scripture) VALUES ({0}, {1}, '{2}');".format(book_num, chapter_num, text))
        cursor.execute(sql)

    def create_bible_from_jped_data(self, cursor, bible):
        count = 0
        for b in range(1, 6):
            book = BibleBooks.abbrev["eng"][str(b)][1]
            chapters = BibleBooks.chapters[b]
            for c in range(1, chapters+1):
                print(f"Processing {book}: {c}")
                chapterData = ""
                verses = BibleBooks.verses[b][c]
                for v in range(1, verses+1):
                    verseData = ""
                    sections = jepd.JPEDSqlite.getVerses(b, c, v, bible)
                    if sections:
                        chapterData += "<verse>"
                        chapterData += ("<vid id=\"v{0}.{1}.{2}\" onclick=\"luV({2})\">{2} "
                                    "</vid>"
                                    ).format(b, c, v)
                        verseData += "<verse>"
                        for section in sections:
                            chapterData += "<span title=\"Source: {0}\" class=\"jepd_{0}\">".format(section[5])
                            chapterData += self.delete_strongs(section[6])
                            chapterData += "</span>"
                            verseData += "<span title=\"Source: {0}\" class=\"jepd_{0}\">".format(section[5])
                            verseData += section[6]
                            verseData += "</span>"
                        chapterData += "</verse>"
                        verseData += "</verse>"
                        self.insert_verse(cursor, b, c, v, verseData)
                    chapterData += "<br><br>\n"
                self.insert_chapter(cursor, b, c, chapterData)

    def create_jepd_bible(self):
        # Step 1 - Create mapping database
        # self.JEPDSqlite.create_mapping_database()

        # Step 2 - Create the raw KJV data from the mapping data
        # self.JPEDSqlite.deleteBibleFromVerses("KJV")
        # self.create_bible_mapping("KJV")

        # Step 3 - Create the JEPD bible from the raw data
        self.create_bible_tables(self.cursorJEPDKJV)
        self.create_bible_from_jped_data(self.cursorJEPDKJV, "KJV")

    def create_headings_authors_doc(self):
        count = 0
        # for b in range(1, 6):
        #     book = BibleBooks.abbrev["eng"][str(b)][1]
        #     chapters = BibleBooks.chapters[b]
        #     for c in range(1, chapters + 1):
        #         verses = BibleBooks.verses[b][c]
        #         for v in range(1, verses + 1):
        #             headingKey = f"{b}.{c}.{v}"
        #             if headingKey in agbSubheadings:
        #                 heading = agbSubheadings[headingKey]
        keys = list(agbSubheadings.keys())
        currentBook = 0
        baseUrl = "https://simple.uniquebibleapp.com/bible/JEPD/"
        for index, (key, heading) in enumerate(agbSubheadings.items()):
            if key.startswith("6."):
                break
            nextKey = keys[index+1]
            b1, c1, v1 = key.split(".")
            b2, c2, v2 = nextKey.split(".")
            endVerse = int(v2) - 1
            if c1 != c2:
                endVerse = BibleBooks.verses[int(b1)][int(c1)]
            if currentBook != int(b1):
                currentBook = int(b1)
                print(BibleBooks.abbrev["eng"][b1][1])
            url = baseUrl + BibleBooks.abbrev["eng"][b1][1] + "/" + c1 + "#v" + c1 + "_" + v1
            print(BibleBooks.abbrev["eng"][b1][1] + " " + c1 + ":" + v1)
            print(f"{url}")
            print(f"{heading}")
            sourceData = self.get_sources_for_verses(b1, c1, v1, endVerse)
            for sIndex, (sKey, sValue) in enumerate(sourceData.items()):
                delimiter = ", " if sIndex < len(sourceData) - 1 else ""
                print(f"{sKey}: {sValue}", end=delimiter)
            print("\n")

    def get_sources_for_verses(self, b, c, vStart, vEnd):
        sourceData = {}
        for v in range(int(vStart), int(vEnd)+1):
            verses = self.JPEDSqlite.getMapping(b, c, v)
            for verse in verses:
                source = verse[5]
                if source not in sourceData.keys():
                    sourceData[source] = 1
                else:
                    sourceData[source] += 1
        return sourceData

if __name__ == "__main__":

    jepd = JEPDUtil()
    jepd.create_headings_authors_doc()
