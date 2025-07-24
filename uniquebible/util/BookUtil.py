
import os, sqlite3, re, platform
import sys

from uniquebible.util.JEPDUtil import JEPDUtil


class BookUtil:

    def __init__(self):
        self.home = '/Users/otseng'


    def set_book_name(self, book_name):
        file = self.home + '/UniqueBible/marvelData/books/' + book_name + '.book'
        self.book = file
        self.connection = sqlite3.connect(self.book)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def create_tables(self):
        # print('Create table')
        self.cursor.execute('CREATE TABLE Reference (Chapter NVARCHAR(100), Content TEXT)')

    def drop_tables(self):
        # print('Drop table')
        self.cursor.execute('DROP TABLE IF EXISTS Reference;')

    def delete_entry(self, chapter):
        self.cursor.execute("DELETE from Reference where Chapter='" + chapter + "'")

    def entry_exists(self, chapter):
        self.cursor.execute("SELECT COUNT(*) from Reference where Chapter='" + chapter + "'")
        count = self.cursor.fetchone()[0]
        if count == 0:
            return False
        else:
            return True

    def insert_chapter(self, chapter, text):
        try:
            text = text.replace("'", "''")
            sql = ("INSERT INTO Reference VALUES ('{0}', '{1}')".format(chapter, text))
            self.cursor.execute(sql)
        except Exception as e:
            print(e)
            print(text)

    def convert_link(self, html):
        html = re.sub("\[(.+?)\]\(.+?\/[gG](\d+)\.md\)", "<a target='_blank' href=\"https://www.blueletterbible.org/lexicon/G\\2\">\\1</a>", html)
        html = re.sub("\[(.+?)\]\(.+?\/[hH](\d+)\.md\)", "<a target='_blank' href=\"https://www.blueletterbible.org/lexicon/H\\2\">\\1</a>", html)
        return html

    def process_jepd_headings_with_sources(self):
        chapter = "Headings with Sources"
        self.delete_entry(chapter)
        jepd = JEPDUtil()
        content = jepd.create_jepd_headings_with_sources()
        self.insert_chapter(chapter, content)

if __name__ == "__main__":
    print("Processing")

    bookUtil = BookUtil()
    bookUtil.set_book_name('JEPD')
    bookUtil.drop_tables()
    bookUtil.create_tables()

    bookUtil.process_jepd_headings_with_sources()

    print("Done")

