import os, sqlite3, re, glob, platform
from pathlib import Path
import sys

from uniquebible.db.JEPDSqlite import JEPDSqlite


# Generate_Transliteration.py
# TRLIT_Bible.py

class JEPDUtil:

    def __init__(self):
        self.home = '/Users/otseng'
        if platform.system() == "Linux":
            self.home = '/home/oliver'
        self.KJVx = self.home + '/UniqueBible/marvelData/bibles/KJVx.bible'
        self.connectionKJVx = sqlite3.connect(self.KJVx)
        self.cursorKJVx = self.connectionKJVx.cursor()
        self.JEPD_KJV_BIBLE = self.home + '/UniqueBible/marvelData/bibles/JEPD_KJV.bible'
        self.connectionJEPD = sqlite3.connect(self.JEPD_KJV_BIBLE)
        self.cursorJEPD = self.connectionJEPD.cursor()
        self.JPEDSqlite = JEPDSqlite()

    def __del__(self):
        self.connectionKJVx.close()
        self.connectionJEPD.close()

    def read_verse(self, cursor, book_num, chapter_num, verse_num):
        sql = 'SELECT * from Verses where Book=' + str(book_num) \
               + ' and Chapter=' + str(chapter_num) + ' and Verse=' + str(verse_num)
        cursor.execute(sql)
        data = self.cursorKJVx.fetchone()
        return data[3]

    def create_jepd_kjv(self):
        pass

if __name__ == "__main__":
    jepd = JEPDUtil()
    jepd.create_jepd_kjv()
