import config
from PySide2.QtCore import QStringListModel
#from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import (QPushButton, QListView, QAbstractItemView, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget)
from ToolsSqlite import Book

class LibraryLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["menu_library"])
        # set up variables
        self.parent = parent
        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout = QGridLayout()

        leftColumnWidget = QGroupBox(config.thisTranslation["commentaries"])
        commentaryLayout = QVBoxLayout()
        commentaryLayout.addWidget(self.commentaryListView())
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(self.openPreviousCommentary)
        commentaryLayout.addWidget(button)
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
        button.clicked.connect(self.fvouriteBookOnly)
        subSubLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["addFavourite"])
        button.clicked.connect(self.parent.parent.addFavouriteBookDialog)
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

    def commentaryListView(self):
        # https://doc.qt.io/archives/qtforpython-5.12/PySide2/QtCore/QStringListModel.html
        # https://gist.github.com/minoue/9f384cd36339429eb0bf
        # https://www.pythoncentral.io/pyside-pyqt-tutorial-qlistview-and-qstandarditemmodel/
        list = QListView()
        list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #model = QStandardItemModel(list)
        #for item in items:
        #    item = QStandardItem(item)
        #    item.setCheckable(True)
        #    model.appendRow(item)
        model = QStringListModel(self.parent.commentaryList)
        list.setModel(model)
        if config.commentaryText in self.parent.commentaryList:
            list.setCurrentIndex(model.index(self.parent.commentaryList.index(config.commentaryText), 0))
        list.selectionModel().selectionChanged.connect(self.commentarySelected)
        return list

    def bookListView(self):
        self.bookList = QListView()
        self.bookList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.bookModel = QStringListModel(self.parent.referenceBookList)
        self.bookList.setModel(self.bookModel)
        if config.book in self.parent.referenceBookList:
            self.bookList.setCurrentIndex(self.bookModel.index(self.parent.referenceBookList.index(config.book), 0))
        self.bookList.selectionModel().selectionChanged.connect(self.bookSelected)
        return self.bookList

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
        return Book(config.book).getTopicList() if config.book in self.parent.referenceBookList else []

    def scrollChapterList(self, topicList):
        self.chapterlist.setCurrentIndex(self.chapterModel.index(topicList.index(config.bookChapter) if topicList and config.bookChapter in topicList else 0, 0))

    def openPreviousCommentary(self):
        command = "COMMENTARY:::{0}:::{1}".format(config.commentaryText, self.parent.bibleTab.getSelectedReference())
        self.parent.runTextCommand(command)

    def openPreviousBookChapter(self):
        command = "BOOK:::{0}:::{1}".format(config.book, config.bookChapter)
        self.parent.runTextCommand(command)

    def commentarySelected(self, selection):
        config.commentaryText = selection[0].indexes()[0].data()
        command = "COMMENTARY:::{0}:::{1}".format(config.commentaryText, self.parent.bibleTab.getSelectedReference())
        self.parent.runTextCommand(command)

    def showAllBooks(self):
        self.bookModel.setStringList(self.parent.referenceBookList)
        self.bookList.setCurrentIndex(self.bookModel.index(0, 0))

    def fvouriteBookOnly(self):
        self.bookModel.setStringList(config.favouriteBooks)
        self.bookList.setCurrentIndex(self.bookModel.index(0, 0))

    def bookSelected(self, selection):
        self.parent.isRefreshing = True
        selectedBook = selection[0].indexes()[0].data()
        if config.book != selectedBook:
            config.book = selectedBook
            topicList = self.getBookTopicList()
            self.chapterModel.setStringList(topicList)
            config.bookChapter = topicList[0] if topicList else ""
            self.scrollChapterList(topicList)

    def chapterSelected(self, selection):
        config.bookChapter = selection[0].indexes()[0].data()
        command = "BOOK:::{0}:::{1}".format(config.book, config.bookChapter)
        if not self.parent.isRefreshing:
            self.parent.runTextCommand(command)
        self.parent.isRefreshing = False
