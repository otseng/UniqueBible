import glob
import os, sqlite3, config, re, logging
from pathlib import Path

from db.BiblesSqlite import BiblesSqlite

if __name__ == "__main__":
    from util.ConfigUtil import ConfigUtil
    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"
    config.noQt = True
    ConfigUtil.setup()
    config.noQt = True

from util.BibleVerseParser import BibleVerseParser
from util.BibleBooks import BibleBooks
from db.NoteSqlite import NoteSqlite
from db.Highlight import Highlight
from util.ConfigUtil import ConfigUtil
from util.FileUtil import FileUtil
from util.themes import Themes
from util.NoteService import NoteService
from util.TextUtil import TextUtil
from util.LexicalData import LexicalData
from db.ToolsSqlite import Commentary


class HtmlContentBuilder:

    def __init__(self):
        self.biblesSqlite = BiblesSqlite()

    def getMenu(self, command, source="main"):
        parser = BibleVerseParser(config.parserStandarisation)
        items = command.split(".", 3)
        text = items[0]
        versions = self.biblesSqlite.getBibleList()
        # provide a link to go back the last opened bible verse
        if source == "study":
            mainVerseReference = parser.bcvToVerseReference(config.studyB, config.studyC, config.studyV)
            menu = "<ref onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; {0} - {1}</ref>".format(config.studyText, mainVerseReference)
        else:
            mainVerseReference = parser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
            menu = "<ref onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; {0} - {1}</ref>".format(config.mainText, mainVerseReference)
        # select bible versions
        menu += "<hr><b>{1}</b> {0}".format(self.biblesSqlite.getTexts(), config.thisTranslation["html_bibles"])
        if text:
            # i.e. text specified; add book menu
            if config.openBibleInMainViewOnly or config.enableHttpServer:
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button>".format(text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_open"])
            else:
                if source == "study":
                    anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openMain"])
                else:
                    anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openStudy"])
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {4}".format(text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_openHere"], anotherView)
            menu += "<hr><b>{1}</b> {0}".format(self.biblesSqlite.getBooks(text), config.thisTranslation["html_book"])
            # create a list of inters b, c, v
            bcList = [int(i) for i in items[1:]]
            if bcList:
                check = len(bcList)
                bookNo = bcList[0]
                engFullBookName = BibleBooks().eng[str(bookNo)][-1]
                engFullBookNameWithoutNumber = engFullBookName
                matches = re.match("^[0-9]+? (.*?)$", engFullBookName)
                if matches:
                    engFullBookNameWithoutNumber = matches.group(1)
                # check book name
                #print(engFullBookName)
                if check >= 1:
                    # i.e. book specified; add chapter menu
                    bookReference = parser.bcvToVerseReference(bookNo, 1, 1)
                    bookAbb = bookReference[:-4]
                    # build open book button
                    if config.openBibleInMainViewOnly or config.enableHttpServer:
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, bookReference, anotherView, config.thisTranslation["html_openHere"])
                    # build search book by book introduction button
                    introductionButton = "<button class='feature' onclick='document.title=\"SEARCHBOOKCHAPTER:::Tidwell_The_Bible_Book_by_Book:::{0}\"'>{1}</button>".format(engFullBookName, config.thisTranslation["html_introduction"])
                    # build search timelines button
                    timelinesButton = "<button class='feature' onclick='document.title=\"SEARCHBOOKCHAPTER:::Timelines:::{0}\"'>{1}</button>".format(engFullBookName, config.thisTranslation["html_timelines"])
                    # build search encyclopedia button
                    encyclopediaButton = "<button class='feature' onclick='document.title=\"SEARCHTOOL:::{0}:::{1}\"'>{2}</button>".format(config.encyclopedia, engFullBookNameWithoutNumber, config.thisTranslation["context1_encyclopedia"])
                    # build search dictionary button
                    dictionaryButton = "<button class='feature' onclick='document.title=\"SEARCHTOOL:::{0}:::{1}\"'>{2}</button>".format(config.dictionary, engFullBookNameWithoutNumber, config.thisTranslation["context1_dict"])
                    # display selected book
                    menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span> {1}<br>{3} {4} {5} {6}".format(bookAbb, openOption, config.thisTranslation["html_current"], introductionButton, timelinesButton, dictionaryButton, encyclopediaButton)

                    # Commentary intros on book

                    commentaries = Commentary().getCommentaryListThatHasBookAndChapter(40, 0)
                    bookCommentaryButton = "<button class='feature' onclick='document.title=\"COMMENTARY:::{0}:::{1}\"'>{2}</button>".format(
                        bookAbb, )

                    # add chapter menu
                    menu += "<hr><b>{1}</b> {0}".format(self.biblesSqlite.getChapters(bookNo, text), config.thisTranslation["html_chapter"])
                if check >= 2:
                    chapterNo = bcList[1]
                    # i.e. both book and chapter specified; add verse menu
                    chapterReference = parser.bcvToVerseReference(bookNo, chapterNo, 1)
                    # build open chapter button
                    if config.openBibleInMainViewOnly or config.enableHttpServer:
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, chapterReference, anotherView, config.thisTranslation["html_openHere"])
                    # overview button
                    overviewButton = "<button class='feature' onclick='document.title=\"OVERVIEW:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_overview"])
                    # chapter index button
                    chapterIndexButton = "<button class='feature' onclick='document.title=\"CHAPTERINDEX:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_chapterIndex"])
                    # summary button
                    summaryButton = "<button class='feature' onclick='document.title=\"SUMMARY:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_summary"])
                    # chapter commentary button
                    chapterCommentaryButton = "<button class='feature' onclick='document.title=\"COMMENTARY:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["menu4_commentary"])
                    # chapter note button
                    chapterNoteButton = " <button class='feature' onclick='document.title=\"_openchapternote:::{0}.{1}\"'>{2}</button>".format(bookNo, chapterNo, config.thisTranslation["menu6_notes"])
                    # selected chapter
                    menu += "<br><br><b>{3}</b> <span style='color: brown;' onmouseover='document.title=\"_info:::Chapter {1}\"'>{1}</span> {2}{4}<br>{5} {6} {7} {8}".format(bookNo, chapterNo, openOption, config.thisTranslation["html_current"], "" if config.enableHttpServer else chapterNoteButton, overviewButton, chapterIndexButton, summaryButton, chapterCommentaryButton)
                    # building verse list of slected chapter
                    menu += "<hr><b>{1}</b> {0}".format(self.biblesSqlite.getVersesMenu(bookNo, chapterNo, text), config.thisTranslation["html_verse"])
                if check == 3:
                    verseNo = bcList[2]
                    if config.openBibleInMainViewOnly or config.enableHttpServer:
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, mainVerseReference, anotherView, config.thisTranslation["html_openHere"])
                    verseNoteButton = " <button class='feature' onclick='document.title=\"_openversenote:::{0}.{1}.{2}\"'>{3}</button>".format(bookNo, chapterNo, verseNo, config.thisTranslation["menu6_notes"])
                    menu += "<br><br><b>{5}</b> <span style='color: brown;' onmouseover='document.title=\"_instantVerse:::{0}:::{1}.{2}.{3}\"'>{3}</span> {4}{6}".format(text, bookNo, chapterNo, verseNo, openOption, config.thisTranslation["html_current"], "" if config.enableHttpServer else verseNoteButton)
                    #menu += "<hr><b>{0}</b> ".format(config.thisTranslation["html_features"])
                    menu += "<br>"
                    features = (
                        ("COMPARE", config.thisTranslation["menu4_compareAll"]),
                        ("CROSSREFERENCE", config.thisTranslation["menu4_crossRef"]),
                        ("TSKE", config.thisTranslation["menu4_tske"]),
                        ("TRANSLATION", config.thisTranslation["menu4_traslations"]),
                        ("DISCOURSE", config.thisTranslation["menu4_discourse"]),
                        ("WORDS", config.thisTranslation["menu4_words"]),
                        ("COMBO", config.thisTranslation["menu4_tdw"]),
                        ("COMMENTARY", config.thisTranslation["menu4_commentary"]),
                        ("INDEX", config.thisTranslation["menu4_indexes"]),
                    )
                    for keyword, description in features:
                        menu += "<button class='feature' onclick='document.title=\"{0}:::{1}\"'>{2}</button> ".format(keyword, mainVerseReference, description)
                    # Compare menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='compare{0}'></div> ".format(version)
                            menu += "<script>versionList.push('{0}');</script>".format(version)
                    menu += "<br><button type='button' onclick='checkCompare();' class='feature'>{0}</button>".format(config.thisTranslation["html_showCompare"])
                    # Parallel menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='parallel{0}'></div> ".format(version)
                    menu += "<br><button type='button' onclick='checkParallel();' class='feature'>{0}</button>".format(config.thisTranslation["html_showParallel"])
                    # Diff menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='diff{0}'></div> ".format(version)
                    menu += "<br><button type='button' onclick='checkDiff();' class='feature'>{0}</button>".format(config.thisTranslation["html_showDifference"])
        else:
            # menu - Search a bible
            if source == "study":
                defaultSearchText = config.studyText
            else:
                defaultSearchText = config.mainText
            menu += "<hr><b>{1}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span>".format(defaultSearchText, config.thisTranslation["html_searchBible2"])
            menu += "<br><br><input type='text' id='bibleSearch' style='width:95%' autofocus><br><br>"
            searchOptions = ("SEARCH", "SEARCHREFERENCE", "SEARCHOT", "SEARCHNT", "SEARCHALL", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
            for searchMode in searchOptions:
                menu += "<button  id='{0}' type='button' onclick='checkSearch(\"{0}\", \"{1}\");' class='feature'>{0}</button> ".format(searchMode, defaultSearchText)
            # menu - Search multiple bibles
            menu += "<hr><b>{0}</b> ".format(config.thisTranslation["html_searchBibles2"])
            for version in versions:
                if version == defaultSearchText or version == config.favouriteBible:
                    menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='search{0}' checked></div> ".format(version)
                else:
                    menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='search{0}'></div> ".format(version)
                menu += "<script>versionList.push('{0}');</script>".format(version)
            menu += "<br><br><input type='text' id='multiBibleSearch' style='width:95%'><br><br>"
            for searchMode in searchOptions:
                menu += "<button id='multi{0}' type='button' onclick='checkMultiSearch(\"{0}\");' class='feature'>{0}</button> ".format(searchMode)
            # Perform search when "ENTER" key is pressed
            menu += self.inputEntered("bibleSearch", "SEARCH")
            menu += self.inputEntered("multiBibleSearch", "multiSEARCH")
        return menu

    def inputEntered(self, inputID, buttonID):
        return """
<script>
var input = document.getElementById('{2}');
input.addEventListener('keyup', function(event) {0}
  if (event.keyCode === 13) {0}
   event.preventDefault();
   document.getElementById('{3}').click();
  {1}
{1});
</script>""".format("{", "}", inputID, buttonID)

    def formTextTag(self, text=config.mainText):
        return "<ref onclick='document.title=\"_menu:::{0}\"' onmouseover='textName(\"{0}\")'>".format(text)

    def formBookTag(self, b, text=config.mainText):
        bookAbb = self.bcvToVerseReference(b, 1, 1)[:-4]
        return "<ref onclick='document.title=\"_menu:::{0}.{1}\"' onmouseover='bookName(\"{2}\")'>".format(text, b,
                                                                                                           bookAbb)

    def formChapterTag(self, b, c, text=config.mainText):
        return "<ref onclick='document.title=\"_menu:::{0}.{1}.{2}\"' onmouseover='document.title=\"_info:::Chapter {2}\"'>".format(
            text, b, c)

    def formVerseTag(self, b, c, v, text=config.mainText):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{3}:::{4}\";' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_menu:::{3}.{0}.{1}.{2}\"'>".format(
            b, c, v, text, verseReference)


    def getVersesMenu(self, b=config.mainB, c=config.mainC, text=config.mainText):
        verseList = self.getVerseList(b, c, text)
        return " ".join(["{0}{1}</ref>".format(self.formVerseTagMenu(b, c, verse, text), verse) for verse in verseList])

    def formVerseTagMenu(self, b, c, v, text=config.mainText):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"_menu:::{3}.{0}.{1}.{2}\"' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_menu:::{3}.{0}.{1}.{2}\"'>".format(b, c, v, text, verseReference)
