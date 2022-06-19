import config
from db.IndexSqlite import IndexSqlite

if __name__ == "__main__":
    config.noQt = True

from db.BiblesSqlite import BiblesSqlite


class IndexerUtil:

    @staticmethod
    def createBibleIndex(bibleName):
        maxBooksToProcess = 1
        debug = True
        biblesSqlite = BiblesSqlite()
        bibleInfo = biblesSqlite.bibleInfo(bibleName)
        indexSqlite = IndexSqlite("bible", bibleName, True)
        if debug:
            indexSqlite.deleteAll()
        if bibleInfo:
            print(f"Creating index for {bibleName}")
            bookList = biblesSqlite.getBookList(bibleName)
            for bookNum in bookList:
                if bookNum > maxBooksToProcess:
                    break
                chapterList = biblesSqlite.getChapterList(bookNum, bibleName)
                print(f"Indexing {bookNum}:{chapterList}")
                for chapterNum in chapterList:
                    verseList = biblesSqlite.getVerseList(bookNum, chapterNum, bibleName)
                    for verseNum in verseList:
                        verseData = biblesSqlite.readTextVerse(bibleName, bookNum, chapterNum, verseNum)
                        words = verseData[3].split()
                        print(f"Inserting {bookNum}:{chapterNum}:{verseNum}:{words}")
                        indexContent = []
                        for word in words:
                            if len(word) > 1:
                                indexContent.append((word, bookNum, chapterNum, verseNum))
                        indexSqlite.insertBibleData(indexContent)
        else:
            print(f"Could not find Bible {bibleName}")

if __name__ == "__main__":

    bibleName = "KJVx"
    IndexerUtil.createBibleIndex(bibleName)
    print("Done")
