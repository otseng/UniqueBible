import config, platform, webbrowser, os
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QMessageBox

class LibraryCatalogDialog(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["libraryCatalog"])
        self.setMinimumSize(500, 500)
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()

    def setupVariables(self):
        self.isUpdating = False
        self.catalogEntryId = None
        self.catalog = [
            ("path/alpha.mp3", "MP3", "path", "alpha.mp3", "music", "repo", "install directory"),
            ("path/alpha.mp4", "MP4", "path", "alpha.mp4", "video", "repo", "install directory"),
            ("path/test.pdf", "PDF", "path", "test.pdf", "pdf", "repo", "install directory"),
            ("path/test.book", "BOOK", "path", "test.book", "books", "repo", "install directory"),
            ]

    def setupUI(self):
        mainLayout = QVBoxLayout()

        filterLayout = QHBoxLayout()
        filterLayout.addWidget(QLabel(config.thisTranslation["menu5_search"]))
        self.filterEntry = QLineEdit()
        self.filterEntry.textChanged.connect(self.resetItems)
        filterLayout.addWidget(self.filterEntry)
        mainLayout.addLayout(filterLayout)

        self.dataView = QTableView()
        self.dataView.clicked.connect(self.itemClicked)
        self.dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dataView.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.dataView)
        self.dataView.setModel(self.dataViewModel)
        self.resetItems()
        # self.dataViewModel.itemChanged.connect(self.itemChanged)
        mainLayout.addWidget(self.dataView)

        buttonLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(self.open)
        buttonLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["download"])
        button.clicked.connect(self.download)
        buttonLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["close"])
        button.clicked.connect(self.close)
        buttonLayout.addWidget(button)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def getCatalogItems(self):
        data = {}
        pdfCount = 0
        mp3Count = 0
        mp4Count = 0
        bookCount = 0
        docxCount = 0
        commCount = 0
        lexCount = 0
        for filename, type, directory, file, description, repo, installDirectory in self.catalog:
            id = "UNKNOWN"
            if type == "PDF":
                pdfCount += 1
                id = "{0}-{1}".format(type, pdfCount)
            elif type == "MP3":
                mp3Count += 1
                id = "{0}-{1}".format(type, mp3Count)
            elif type == "MP4":
                mp4Count += 1
                id = "{0}-{1}".format(type, mp4Count)
            elif type == "BOOK":
                bookCount += 1
                id = "{0}-{1}".format(type, bookCount)
            elif type == "DOCX":
                docxCount += 1
                id = "{0}-{1}".format(type, docxCount)
            elif type == "COMM":
                commCount += 1
                id = "{0}-{1}".format(type, commCount)
            elif type == "LEX":
                lexCount += 1
                id = "{0}-{1}".format(type, lexCount)
            data[id] = [id, filename, type, directory, file, description, repo, installDirectory]
        return data

    def resetItems(self):
        self.isUpdating = True
        # Empty the model before reset
        self.dataViewModel.clear()
        # Reset
        self.catalogData = self.getCatalogItems()
        filterEntry = self.filterEntry.text().lower()
        rowCount = 0
        colCount = 0
        for id, value in self.catalogData.items():
            id2, filename, type, directory, file, description, repo, installDirectory = value
            if filterEntry == "" or (filterEntry in filename.lower() or filterEntry in description.lower()):
                item = QStandardItem(id)
                self.dataViewModel.setItem(rowCount, colCount, item)
                colCount += 1
                item = QStandardItem(file)
                self.dataViewModel.setItem(rowCount, colCount, item)
                colCount += 1
                # item = QStandardItem(type)
                # self.dataViewModel.setItem(rowCount, colCount, item)
                # colCount += 1
                # item = QStandardItem(directory)
                # self.dataViewModel.setItem(rowCount, colCount, item)
                # colCount += 1
                # item = QStandardItem(description)
                # self.dataViewModel.setItem(rowCount, colCount, item)
                # colCount += 1
                # add row count
                rowCount += 1
                colCount = 0
        self.dataViewModel.setHorizontalHeaderLabels(
            ["#", config.thisTranslation["file"],
             # config.thisTranslation["type"], config.thisTranslation["directory"],
             # config.thisTranslation["description"]
             ])
        self.dataView.resizeColumnsToContents()
        self.isUpdating = False

    # def itemChanged(self, standardItem):
    #     flag = standardItem.text()
    #     if flag in self.catalogData and not self.isUpdating:
    #         self.catalogData[flag][-1]()

    def itemClicked(self, index):
        self.selectedRow = index.row()
        self.catalogEntryId = self.dataViewModel.item(self.selectedRow, 0).text()

    def displayMessage(self, message="", title="UniqueBible"):
        QMessageBox.information(self, title, message)

    def open(self):
        pass

    def download(self):
        pass


## Standalone development code

class DummyParent():
    def runTextCommand(self, command):
        print(command)

    def verseReference(self, command):
        return ['', '']

if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication
    from qtpy.QtCore import QCoreApplication
    from util.ConfigUtil import ConfigUtil
    from util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.noQt = False
    config.bibleCollections["Custom"] = ['ABP', 'ACV']
    config.bibleCollections["King James"] = ['KJV', 'KJVx', 'KJVA', 'KJV1611', 'KJV1769x']
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    dialog = LibraryCatalogDialog(DummyParent())
    dialog.exec_()