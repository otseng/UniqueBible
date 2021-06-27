import config
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QMessageBox


class BibleCollectionWindow(QDialog):

    def __init__(self):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["bibleCollection"])
        self.setMinimumSize(500, 500)
        self.bibles = self.getBibles()
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()

    def setupVariables(self):
        self.isUpdating = False

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["bibleCollection"])
        mainLayout.addWidget(title)

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
        bibles = BiblesSqlite().getBibleList()
        return bibles

    def itemChanged(self, standardItem):
        pass

    def resetItems(self):
        self.isUpdating = True
        # Empty the model before reset
        self.dataViewModel.clear()
        rowCount = 0
        for bible in self.bibles:
            # 1st column
            item = QStandardItem(bible)
            item.setToolTip(bible)
            item.setCheckable(True)
            # item.setCheckState(Qt.CheckState.Checked if configValue else Qt.CheckState.Unchecked)
            self.dataViewModel.setItem(rowCount, 0, item)
            # 2nd column
            # item = QStandardItem(str(default))
            # self.dataViewModel.setItem(rowCount, 1, item)
            # # 3rd column
            # tooltip = tooltip.replace("\n", " ")
            # item = QStandardItem(tooltip)
            # item.setToolTip(tooltip)
            # self.dataViewModel.setItem(rowCount, 2, item)
            # add row count
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels([config.thisTranslation["bible"], config.thisTranslation["description"]])
        self.dataView.resizeColumnsToContents()
        self.isUpdating = False

    def displayMessage(self, message="", title="UniqueBible"):
        QMessageBox.information(self, title, message)


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