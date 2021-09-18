import os

import config
from qtpy.QtCore import QStringListModel
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import (QPushButton, QListView, QAbstractItemView, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget)
from db.ToolsSqlite import Book, BookData, Commentary
from util.FileUtil import FileUtil


class LibraryLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["menu_library"])
        # set up variables
        self.parent = parent
        # setup interface
        self.setupUI()
        self.selectedBook = None

    def setupUI(self):
        mainLayout = QGridLayout()

        leftColumnWidget = QGroupBox(config.thisTranslation["commentaries"])
        commentaryLayout = QVBoxLayout()
        commentaryLayout.addWidget(self.commentaryListView())
        subSubLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(self.openPreviousCommentary)
        subSubLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["activeOnly"])
        button.clicked.connect(self.showActiveOnlyCommentaries)
        subSubLayout.addWidget(button)
        commentaryLayout.addLayout(subSubLayout)

        leftColumnWidget.setLayout(commentaryLayout)

        rightColumnWidget = QGroupBox(config.thisTranslation["menu10_books"])
        bookLayout = QHBoxLayout()
        subLayout = QVBoxLayout()
        subLayout.addWidget(self.bookListView())

        subSubLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["showAll"])
        button.clicked.connect(self.showAllBooks)
        subSubLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["favouriteOnly"])
        button.clicked.connect(self.favouriteBookOnly)
        subSubLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["addFavourite"])
        button.clicked.connect(self.addFavorite)
        subSubLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["removeFavourite"])
        button.clicked.connect(self.removeFavorite)
        subSubLayout.addWidget(button)
        subLayout.addLayout(subSubLayout)
        bookLayout.addLayout(subLayout)

        subLayout = QVBoxLayout()
        subLayout.addWidget(self.chapterListView())
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(self.openPreviousBookChapter)
        subLayout.addWidget(button)
        bookLayout.addLayout(subLayout)
        rightColumnWidget.setLayout(bookLayout)

        mainLayout.addWidget(leftColumnWidget, 0, 0)
        mainLayout.addWidget(rightColumnWidget, 0, 1)
        mainLayout.setColumnStretch(1, 2)
        self.setLayout(mainLayout)

    def testChecked(self, test):
        print(test)

    def commentaryListView(self):
        # https://doc.qt.io/archives/qtforpython-5.12/PySide2/QtCore/QStringListModel.html
        # https://gist.github.com/minoue/9f384cd36339429eb0bf
        # https://www.pythoncentral.io/pyside-pyqt-tutorial-qlistview-and-qstandarditemmodel/
        self.commentaryListView = QListView()
        self.commentaryListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.reloadCommentariesListModel()
        return self.commentaryListView

    def reloadCommentariesListModel(self, showOnlyActiveCommentaries=False):
        self.commentaryList = []
        activeCommentaries = []
        if showOnlyActiveCommentaries:
            activeCommentaries = [item[1] for item in Commentary().getCommentaryListThatHasBookAndChapter(config.mainB, config.mainC)]
        for index, commentary in enumerate(self.parent.commentaryFullNameList):
            if not showOnlyActiveCommentaries or commentary in activeCommentaries:
                # item = QStandardItem(commentary)
                # item.setToolTip(self.parent.commentaryList[index])
                self.commentaryList.append(commentary)
        model = QStringListModel(self.commentaryList)
        self.commentaryListView.setModel(model)
        if config.commentaryText in self.commentaryList:
            self.commentaryListView.setCurrentIndex(model.index(self.commentaryList.index(config.commentaryText), 0))
        self.commentaryListView.selectionModel().selectionChanged.connect(self.commentarySelected)


    def bookListView(self):
        self.bookList = QListView()
        self.bookList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.reloadBookListModel()
        return self.bookList


    def reloadBookListModel(self, files=None):
        self.dirsAndFiles = self.getSubdirectories()
        if files is None:
            self.dirsAndFiles += BookData().getBooks()
        else:
            books = BookData().getBooks()
            for file in files:
                if file in books:
                    self.dirsAndFiles.append(file)
        self.bookModel = QStringListModel(self.dirsAndFiles)
        self.bookList.setModel(self.bookModel)
        if config.book in self.dirsAndFiles:
            self.bookList.setCurrentIndex(self.bookModel.index(self.dirsAndFiles.index(config.book), 0))
        self.bookList.selectionModel().selectionChanged.connect(self.bookOrFileSelected)

    def getSubdirectories(self):
        return ["../"] + BookData().getDirectories()

    def chapterListView(self):
        self.chapterlist = QListView()
        self.chapterlist.setEditTriggers(QAbstractItemView.NoEditTriggers)
        topicList = self.getBookTopicList()
        self.chapterModel = QStringListModel(topicList)
        self.chapterlist.setModel(self.chapterModel)
        self.scrollChapterList(topicList)
        self.chapterlist.selectionModel().selectionChanged.connect(self.chapterSelected)
        return self.chapterlist

    def getBookTopicList(self):
        return Book(config.book).getTopicList()

    def scrollChapterList(self, topicList):
        self.chapterlist.setCurrentIndex(self.chapterModel.index(topicList.index(config.bookChapter) if topicList and config.bookChapter in topicList else 0, 0))

    def openPreviousCommentary(self):
        command = "COMMENTARY:::{0}:::{1}".format(config.commentaryText, self.parent.bibleTab.getSelectedReference())
        self.parent.runTextCommand(command)

    def openPreviousBookChapter(self):
        if config.bookChapter == "":
            config.bookChapter = self.getBookTopicList()[0]
        command = "BOOK:::{0}:::{1}".format(config.book, config.bookChapter)
        self.parent.runTextCommand(command)

    def commentarySelected(self, selection):
        index = selection[0].indexes()[0].row()
        reverseLookup = {v: k for k, v in Commentary.fileLookup.items()}
        config.commentaryText = reverseLookup[self.commentaryList[index]]
        command = "COMMENTARY:::{0}:::{1}".format(config.commentaryText, self.parent.bibleTab.getSelectedReference())
        self.parent.runTextCommand(command)

    def showActiveOnlyCommentaries(self):
        self.reloadCommentariesListModel(True)

    def showAllBooks(self):
        self.reloadBookListModel()

    def favouriteBookOnly(self):
        self.reloadBookListModel(sorted(config.favouriteBooks))

    def bookOrFileSelected(self, selection):
        self.parent.isRefreshing = True
        self.selectedBook = selection[0].indexes()[0].data()
        if config.book != self.selectedBook:
            if self.selectedBook.endswith("/"):
                config.booksFolder = FileUtil.normalizePath(os.path.join(config.booksFolder, self.selectedBook))
                self.reloadBookListModel()
            else:
                config.book = self.selectedBook
                topicList = self.getBookTopicList()
                self.chapterModel.setStringList(topicList)
                config.bookChapter = topicList[0] if topicList else ""
                self.scrollChapterList(topicList)
                command = "SEARCHBOOK:::{0}:::".format(config.book)
                self.parent.commandField.setText(command)

    def addFavorite(self):
        if self.selectedBook and self.selectedBook not in config.favouriteBooks:
            config.favouriteBooks.append(self.selectedBook)
            self.reloadBookListModel(sorted(config.favouriteBooks))

    def removeFavorite(self):
        if self.selectedBook and self.selectedBook in config.favouriteBooks:
            config.favouriteBooks.remove(self.selectedBook)
            self.reloadBookListModel(sorted(config.favouriteBooks))

    def chapterSelected(self, selection):
        config.bookSearchString = ''
        config.bookChapter = selection[0].indexes()[0].data()
        if self.selectedBook:
            config.book = self.selectedBook
        command = "BOOK:::{0}:::{1}".format(config.book, config.bookChapter)
        if not self.parent.isRefreshing:
            self.parent.runTextCommand(command)
        self.parent.isRefreshing = False
