import config, platform, webbrowser, os
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QMessageBox

class LibraryCatalogDialog(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle("Library Catalog")
        # self.setWindowTitle(config.thisTranslation["menu_config_flags"])
        self.setMinimumSize(830, 500)
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()

    def setupVariables(self):
        self.isUpdating = False

    def setupUI(self):
        mainLayout = QVBoxLayout()

        filterLayout = QHBoxLayout()
        filterLayout.addWidget(QLabel(config.thisTranslation["menu5_search"]))
        self.filterEntry = QLineEdit()
        self.filterEntry.textChanged.connect(self.resetItems)
        filterLayout.addWidget(self.filterEntry)
        mainLayout.addLayout(filterLayout)

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
        button = QPushButton(config.thisTranslation["restoreAllDefaults"])
        button.clicked.connect(self.restoreAllDefaults)
        buttonLayout.addWidget(button)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def getOptions(self):
        options = [
            ("showControlPanelOnStartup", config.showControlPanelOnStartup, self.resetItems, False, config.thisTranslation["showControlPanelOnStartup"]),
            ]
        data = {}
        for flag, configValue, action, default, tooltip in options:
            data[flag] = [configValue, default, tooltip, action]
        return data

    def restoreAllDefaults(self):
        for key, value in self.data.items():
            code = "config.{0} = {1}".format(key, value[1])
            exec(code)
        self.resetItems()
        self.displayMessage(config.thisTranslation["message_restart"])

    def itemChanged(self, standardItem):
        flag = standardItem.text()
        if flag in self.data and not self.isUpdating:
            self.data[flag][-1]()

    def resetItems(self):
        self.isUpdating = True
        # Empty the model before reset
        self.dataViewModel.clear()
        # Reset
        self.data = self.getOptions()
        filterEntry = self.filterEntry.text().lower()
        rowCount = 0
        for flag, value in self.data.items():
            configValue, default, tooltip, *_ = value
            if filterEntry == "" or (filterEntry != "" and (filterEntry in flag.lower() or filterEntry in tooltip.lower())):
                # 1st column
                item = QStandardItem(flag)
                item.setToolTip(tooltip)
                item.setCheckable(True)
                item.setCheckState(Qt.CheckState.Checked if configValue else Qt.CheckState.Unchecked)
                self.dataViewModel.setItem(rowCount, 0, item)
                # 2nd column
                item = QStandardItem(str(default))
                self.dataViewModel.setItem(rowCount, 1, item)
                # 3rd column
                tooltip = tooltip.replace("\n", " ")
                item = QStandardItem(tooltip)
                item.setToolTip(tooltip)
                self.dataViewModel.setItem(rowCount, 2, item)
                # add row count
                rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels([config.thisTranslation["flag"], config.thisTranslation["default"], config.thisTranslation["description"]])
        self.dataView.resizeColumnsToContents()
        self.isUpdating = False

    def displayMessage(self, message="", title="UniqueBible"):
        QMessageBox.information(self, title, message)


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