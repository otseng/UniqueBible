import config
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
from qtpy.QtWidgets import QBoxLayout, QLineEdit


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

        newCollectionLayout = QHBoxLayout()
        collectionCodeLabel = QLabel("Code")
        newCollectionLayout.addWidget(collectionCodeLabel)
        self.collectionCode = QLineEdit()
        self.collectionCode.setFixedWidth(100)
        newCollectionLayout.addWidget(self.collectionCode)
        collectionDescriptionLabel = QLabel("Description")
        newCollectionLayout.addWidget(collectionDescriptionLabel)
        self.collectionDescription = QLineEdit()
        self.collectionDescription.setFixedWidth(300)
        newCollectionLayout.addWidget(self.collectionDescription)
        addButton = QPushButton(config.thisTranslation["add"])
        addButton.setFixedWidth(100)
        # addButton.clicked.connect(self.searchLineEntered)
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