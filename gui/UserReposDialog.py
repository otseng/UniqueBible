import os
import config
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import QMessageBox
    from PySide6.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
    from PySide6.QtWidgets import QFileDialog
    from PySide6.QtWidgets import QDialogButtonBox
else:
    from qtpy.QtCore import Qt
    from qtpy.QtGui import QStandardItemModel, QStandardItem
    from qtpy.QtWidgets import QMessageBox
    from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
    from qtpy.QtWidgets import QFileDialog
    from qtpy.QtWidgets import QDialogButtonBox
from db.UserRepoSqlite import UserRepoSqlite
from gui.MultiLineInputDialog import MultiLineInputDialog

class UserReposDialog(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # self.setWindowTitle(config.thisTranslation["userDefinedResources"])
        self.setWindowTitle("User Defined Resources")
        self.setMinimumSize(400, 400)
        self.db = UserRepoSqlite()
        self.userRepos = None
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()

        # title = QLabel(config.thisTranslation["userDefinedResources"])
        title = QLabel("User Defined Resources")
        mainLayout.addWidget(title)

        self.reposTable = QTableView()
        self.reposTable.setEnabled(True)
        self.reposTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.reposTable.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.reposTable)
        self.reposTable.setModel(self.dataViewModel)
        self.dataViewModel.itemChanged.connect(self.repoSelectionChanged)
        self.selectionModel = self.reposTable.selectionModel()
        self.selectionModel.selectionChanged.connect(self.handleSelection)
        mainLayout.addWidget(self.reposTable)
        self.reloadFilters()

        buttonsLayout = QHBoxLayout()
        clearButton = QPushButton(config.thisTranslation["clear"])
        clearButton.clicked.connect(self.clearFilter)
        buttonsLayout.addWidget(clearButton)
        addButton = QPushButton(config.thisTranslation["add"])
        addButton.clicked.connect(self.addNewFilter)
        buttonsLayout.addWidget(addButton)
        removeButton = QPushButton(config.thisTranslation["remove"])
        removeButton.clicked.connect(self.removeFilter)
        buttonsLayout.addWidget(removeButton)
        editButton = QPushButton(config.thisTranslation["edit"])
        editButton.clicked.connect(self.editFilter)
        buttonsLayout.addWidget(editButton)
        mainLayout.addLayout(buttonsLayout)

        buttonsLayout = QHBoxLayout()
        importButton = QPushButton(config.thisTranslation["import"])
        importButton.clicked.connect(self.importFile)
        buttonsLayout.addWidget(importButton)
        exportButton = QPushButton(config.thisTranslation["export"])
        exportButton.clicked.connect(self.exportFile)
        buttonsLayout.addWidget(exportButton)
        buttonsLayout.addStretch()
        mainLayout.addLayout(buttonsLayout)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.close)
        self.buttonBox.rejected.connect(self.reject)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

    def close(self):
        pass

    def reloadFilters(self):
        self.userRepos = self.db.getAll()
        self.dataViewModel.clear()
        rowCount = 0
        for id, active, name, type, directory, repo in self.userRepos:
            item = QStandardItem(name)
            item.setToolTip(name)
            # item.setCheckable(True)
            self.dataViewModel.setItem(rowCount, 0, item)
            item = QStandardItem(repo)
            self.dataViewModel.setItem(rowCount, 1, item)
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels(["Name", "Repo"])
        self.reposTable.resizeColumnsToContents()

    def handleSelection(self, selected, deselected):
        for item in selected:
            row = item.indexes()[0].row()
            filter = self.dataViewModel.item(row, 0)
            self.selectedFilter = filter.text()
            pattern = self.dataViewModel.item(row, 1)
            self.selectedPattern = pattern.text()

    def repoSelectionChanged(self, item):
        pass

    def addNewFilter(self):
        fields = [(config.thisTranslation["filter2"], ""),
                  (config.thisTranslation["pattern"], "")]
        dialog = MultiLineInputDialog("New Filter", fields)
        if dialog.exec():
            data = dialog.getInputs()
            self.db.insert(data[0], data[1])
            self.reloadFilters()

    def removeFilter(self):
        reply = QMessageBox.question(self, "Delete",
                                     'Delete {0} {1}'.format(self.selectedFilter, config.thisTranslation["filter2"]),
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete(self.selectedFilter)
            self.reloadFilters()

    def editFilter(self):
        fields = [(config.thisTranslation["filter2"], self.selectedFilter),
                  (config.thisTranslation["pattern"], self.selectedPattern)]
        dialog = MultiLineInputDialog("Edit Filter", fields)
        if dialog.exec():
            data = dialog.getInputs()
            self.db.delete(self.selectedFilter)
            self.db.insert(data[0], data[1])
            self.reloadFilters()

    def clearFilter(self):
        for index in range(self.dataViewModel.rowCount()):
            item = self.dataViewModel.item(index)
            item.setCheckState(Qt.CheckState.Unchecked)
        self.runFilter()

    def importFile(self):
        options = QFileDialog.Options()
        filename, filtr = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["import"],
                                                      config.thisTranslation["liveFilter"],
                                                      "File (*.filter)",
                                                      "", options)
        if filename:
            try:
                with open(filename, errors='ignore') as f:
                    for line in f:
                        data = line.split(":::")
                        filter = data[0].strip()
                        pattern = data[1].strip()
                        if self.db.checkFilterExists(filter):
                            self.db.delete(filter)
                        self.db.insert(filter, pattern)
            except Exception as e:
                print(e)
            self.reloadFilters()

    def exportFile(self):
        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getSaveFileName(self,
                                           config.thisTranslation["export"],
                                           config.thisTranslation["liveFilter"],
                                           "File (*.filter)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".filter"
            data = ""
            for name, description in self.db.getAll():
                data += f"{name}:::{description}\n"
            f = open(fileName, "w", encoding="utf-8")
            f.write(data)
            f.close()


class Dummy:

    def __init__(self):
        pass

    def disableBiblesInParagraphs(self):
        pass

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
    dialog = UserReposDialog(Dummy())
    dialog.exec_()