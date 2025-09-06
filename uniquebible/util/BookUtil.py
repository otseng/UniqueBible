
import sqlite3, re
from uniquebible.db import JEPDData
from uniquebible.util.BibleBooks import BibleBooks

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

    def process_jepd_books_and_sources(self):
        chapter = "Books and sources"
        self.delete_entry(chapter)
        jepd = JEPDUtil()
        baseUrl = "https://simple.uniquebibleapp.com/bible/JEPD/"
        content = ""
        content += jepd.jepd_styles()
        content += jepd.table_of_contents()
        data = JEPDData.jepd
        for book, bookData in data.items():
            bookName = BibleBooks.abbrev["eng"][book][1]
            content += "<table>\n<tr><td colspan=10 style='text-align: center;'>\n"
            content += f"<h2><a name='{bookName}'>{bookName}</a></h2>\n"
            content += "</td></tr>\n"
            content += "<tr>"
            for source, info in bookData.items():
                content += f"<td style='text-align: center;'><span class='jepd_{source}'>{source}</span></td>\n"
            content += "</tr><tr>\n"
            for source, info in bookData.items():
                content += "<td valign='top'>"
                lines = info.splitlines()
                for line in lines:
                    line = line.replace(",", "").strip()
                    if (line):
                        if line[-1] == ".":
                            line = line[0:-1]
                        match = re.match(f"\d*:\d*", line)
                        verse = match.group()
                        c, v = verse.split(":")
                        url = baseUrl + BibleBooks.abbrev["eng"][book][1] + f"/{c}#{c}_{v}"
                        content += f"<a href='{url}'>{line}</a><br>\n"
                content += "</td>"
            content += "</tr>"
            content += "</table>"
        self.insert_chapter(chapter, content)

    def process_jepd_headings_and_sources(self):
        chapter = "Headings and sources"
        self.delete_entry(chapter)
        jepd = JEPDUtil()
        content = jepd.create_jepd_headings_and_sources()
        self.insert_chapter(chapter, content)

if __name__ == "__main__":
    print("Processing")

    bookUtil = BookUtil()
    bookUtil.set_book_name('JEPD')
    # bookUtil.drop_tables()
    # bookUtil.create_tables()

    # bookUtil.process_jepd_books_and_sources()
    # bookUtil.process_jepd_headings_and_sources()

    print("Done")

