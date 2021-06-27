import config
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
from qtpy.QtWidgets import QInputDialog
from qtpy.QtWidgets import QRadioButton
from qtpy.QtWidgets import QListWidget


class BibleCollectionWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["bibleCollections"])
        self.setMinimumSize(600, 500)
        self.bibles = self.getBibles()
        self.setupUI()
        self.selectedCollection = None

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["bibleCollections"])
        mainLayout.addWidget(title)

        self.collectionsLayout = QVBoxLayout()
        self.collectionsList = QListWidget()
        self.collectionsList.setMaximumHeight(70)
        self.collectionsLayout.addWidget(self.collectionsList)
        mainLayout.addLayout(self.collectionsLayout)
        self.showListOfCollections()

        buttonsLayout = QHBoxLayout()
        addButton = QPushButton(config.thisTranslation["add"])
        # addButton.setFixedWidth(70)
        addButton.clicked.connect(self.addNewCollection)
        buttonsLayout.addWidget(addButton)
        removeButton = QPushButton(config.thisTranslation["remove"])
        # removeButton.setFixedWidth(70)
        removeButton.clicked.connect(self.removeCollection)
        buttonsLayout.addWidget(removeButton)
        buttonsLayout.addStretch()
        mainLayout.addLayout(buttonsLayout)

        self.biblesTable = QTableView()
        self.biblesTable.setEnabled(False)
        self.biblesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.biblesTable.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.biblesTable)
        self.biblesTable.setModel(self.dataViewModel)
        self.resetItems()
        self.dataViewModel.itemChanged.connect(self.bibleSelectionChanged)
        mainLayout.addWidget(self.biblesTable)

        buttonLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["close"])
        button.clicked.connect(self.close)
        buttonLayout.addWidget(button)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def showListOfCollections(self):
        self.collectionsList.clear()
        if len(config.bibleCollections) > 0:
            for collection in config.bibleCollections.keys():
                showBibleSelection = QRadioButton()
                showBibleSelection.setChecked(False)
                self.collectionsList.itemClicked.connect(self.selectCollection)
                self.collectionsList.addItem(collection)
        else:
            self.collectionsList.addItem("[No collection defined]")

    def addNewCollection(self):
        name, ok = QInputDialog.getText(self, 'Collection', 'Collection name:')
        if ok:
            config.bibleCollections[name] = {}
            self.showListOfCollections()

    def removeCollection(self):
        config.bibleCollections.pop(self.selectedCollection, None)
        self.showListOfCollections()
        self.biblesTable.setEnabled(False)

    def getBibles(self):
        from db.BiblesSqlite import BiblesSqlite
        from db.BiblesSqlite import Bible

        bibles = BiblesSqlite().getBibleList()
        bibleInfo = []
        for bible in bibles:
            description = Bible(bible).bibleInfo()
            bibleInfo.append((bible, description))
        return bibleInfo

    def selectCollection(self, item):
        self.selectedCollection = item.text()
        self.biblesTable.setEnabled(True)

    def bibleSelectionChanged(self, item):
        print(item.text())

    def resetItems(self):
        # Empty the model before reset
        self.dataViewModel.clear()
        rowCount = 0
        for bible, description in self.bibles:
            # 1st column
            item = QStandardItem(bible)
            item.setToolTip(bible)
            item.setCheckable(True)
            # item.setCheckState(Qt.CheckState.Checked if configValue else Qt.CheckState.Unchecked)
            self.dataViewModel.setItem(rowCount, 0, item)
            # 2nd column
            item = QStandardItem(description)
            self.dataViewModel.setItem(rowCount, 1, item)
            # # 3rd column
            # tooltip = tooltip.replace("\n", " ")
            # item = QStandardItem(tooltip)
            # item.setToolTip(tooltip)
            # self.dataViewModel.setItem(rowCount, 2, item)
            # add row count
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels([config.thisTranslation["bible"], config.thisTranslation["description"]])
        self.biblesTable.resizeColumnsToContents()


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication
    from qtpy.QtCore import QCoreApplication
    from util.ConfigUtil import ConfigUtil
    from util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.noQt = False
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = BibleCollectionWindow()
    window.exec_()