import os
import config
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QMessageBox
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
from qtpy.QtWidgets import QFileDialog
from qtpy.QtWidgets import QDialogButtonBox
from db.LiveFilterSqlite import LiveFilterSqlite
from gui.MultiLineInputDialog import MultiLineInputDialog


class LiveFilterDialog(QDialog):

    JS_HIDE = """
            count = 0;
            searchResultCount = document.getElementById("searchResultCount");
            divs = document.querySelectorAll("div");
            for (var i = 0, len = divs.length; i < len; i++) {{
                div = divs[i];
                div.hidden = {0};
                count++;
            }};
            if (searchResultCount) {{
                searchResultCount.innerHTML = count;
            }}
            """

    JS_SHOW = """
            wordSets = [{0}];
            count = 0;
            searchResultCount = document.getElementById("searchResultCount");
            divs = document.querySelectorAll("div");
            for (var i=0, len=divs.length; i < len; i++) {{
                div = divs[i];
                var found = true;
                for (var j=0, len2=wordSets.length; j < len2; j++) {{
                    wordSet = wordSets[j];
                    var regex;
                    if (wordSet.startsWith("'")) {{
                        wordSet = wordSet.replace("'", "");
                        wordSet = wordSet.replace("'", "");
                        regex = new RegExp(wordSet);
                    }} else {{
                        regex = new RegExp(wordSet, "i");
                    }}
                    found &= regex.test(div.innerHTML);
                }}
                if (found) {{
                    div.hidden = false;
                    count++;
                }}
            }};
            if (searchResultCount) {{
                searchResultCount.innerHTML = count;
            }}
            """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["liveFilter"])
        self.setMinimumSize(400, 400)
        self.selectedFilter = None
        self.selectedPattern = None
        self.settingBibles = False
        self.db = LiveFilterSqlite()
        self.filters = None
        self.saveReadFormattedBibles = config.readFormattedBibles
        if config.readFormattedBibles:
            self.parent.disableBiblesInParagraphs()
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["liveFilter"])
        mainLayout.addWidget(title)

        self.filtersTable = QTableView()
        self.filtersTable.setEnabled(True)
        self.filtersTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.filtersTable.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.filtersTable)
        self.filtersTable.setModel(self.dataViewModel)
        self.dataViewModel.itemChanged.connect(self.filterSelectionChanged)
        self.selectionModel = self.filtersTable.selectionModel()
        self.selectionModel.selectionChanged.connect(self.handleSelection)
        mainLayout.addWidget(self.filtersTable)
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
        self.filters = self.db.getAll()
        self.dataViewModel.clear()
        rowCount = 0
        for name, description in self.filters:
            item = QStandardItem(name)
            item.setToolTip(name)
            item.setCheckable(True)
            self.dataViewModel.setItem(rowCount, 0, item)
            item = QStandardItem(description)
            self.dataViewModel.setItem(rowCount, 1, item)
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels([config.thisTranslation["filter2"],
                                                      config.thisTranslation["pattern"]])
        self.filtersTable.resizeColumnsToContents()

    def handleSelection(self, selected, deselected):
        for item in selected:
            row = item.indexes()[0].row()
            filter = self.dataViewModel.item(row, 0)
            self.selectedFilter = filter.text()
            pattern = self.dataViewModel.item(row, 1)
            self.selectedPattern = pattern.text()

    def filterSelectionChanged(self, item):
        try:
            numChecked = 0
            for index in range(self.dataViewModel.rowCount()):
                item = self.dataViewModel.item(index)
                if item.checkState() == Qt.Checked:
                    numChecked += 1
            if numChecked == 0:
                config.mainWindow.studyPage.runJavaScript(self.JS_HIDE.format("false"))
            else:
                config.mainWindow.studyPage.runJavaScript(self.JS_HIDE.format("true"))
                self.runFilter()
        except Exception as e:
            print(str(e))

    def runFilter(self):
        sets = []
        for index in range(self.dataViewModel.rowCount()):
            item = self.dataViewModel.item(index)
            if item.checkState() == Qt.Checked:
                sets.append('"{0}"'.format(self.filters[index][1]))
        wordSets = ",".join(sets)
        js = self.JS_SHOW.format(wordSets)
        config.mainWindow.studyPage.runJavaScript(js)

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
    dialog = LiveFilterDialog(Dummy())
    dialog.exec_()