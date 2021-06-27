import config
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
from qtpy.QtWidgets import QInputDialog
from qtpy.QtWidgets import QFormLayout
from qtpy.QtWidgets import QRadioButton


class BibleCollectionWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["bibleCollections"])
        self.setMinimumSize(700, 500)
        self.bibles = self.getBibles()
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["bibleCollections"])
        mainLayout.addWidget(title)

        self.collectionsLayout = QFormLayout()
        mainLayout.addLayout(self.collectionsLayout)
        self.showListOfCollections()

        newCollectionLayout = QHBoxLayout()
        addButton = QPushButton(config.thisTranslation["add"])
        addButton.setFixedWidth(70)
        addButton.clicked.connect(self.addNewCollection)
        newCollectionLayout.addWidget(addButton)
        newCollectionLayout.addStretch()
        mainLayout.addLayout(newCollectionLayout)

        self.dataView = QTableView()
        self.dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dataView.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.dataView)
        self.dataView.setModel(self.dataViewModel)
        self.resetItems()
        self.dataViewModel.itemChanged.connect(self.itemChanged)
        mainLayout.addWidget(self.dataView)

        buttonLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["close"])
        button.clicked.connect(self.close)
        buttonLayout.addWidget(button)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def showListOfCollections(self):
        if len(config.bibleCollections) > 0:
            for collection in config.bibleCollections.keys():
                showBibleSelection = QRadioButton()
                showBibleSelection.setChecked(False)
                # self.showBibleSelection.clicked.connect(lambda: self.selectRadio("bible"))
                self.collectionsLayout.addRow(showBibleSelection, QLabel(collection))
        else:
            self.collectionsLayout.addRow(QLabel("No collections defined"))

    def addNewCollection(self):
        name, ok = QInputDialog.getText(self, 'Collection', 'Collection name:')
        if ok:
            config.bibleCollections[name] = {}
            self.showListOfCollections()

    def getBibles(self):
        from db.BiblesSqlite import BiblesSqlite
        from db.BiblesSqlite import Bible

        bibles = BiblesSqlite().getBibleList()
        bibleInfo = []
        for bible in bibles:
            description = Bible(bible).bibleInfo()
            bibleInfo.append((bible, description))
        return bibleInfo

    def itemChanged(self, standardItem):
        pass

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
        self.dataView.resizeColumnsToContents()


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