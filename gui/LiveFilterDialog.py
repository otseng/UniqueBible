
import config
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
from qtpy.QtWidgets import QInputDialog
from qtpy.QtWidgets import QRadioButton
from qtpy.QtWidgets import QListWidget
from qtpy.QtWidgets import QDialogButtonBox
from gui.CheckableComboBox import CheckableComboBox


class LiveFilterDialog(QDialog):

    JS_HIDE = """
            divs = document.querySelectorAll("div");
            for (var i = 0, len = divs.length; i < len; i++) {{
                div = divs[i];
                div.hidden = {0};
            }};
            """

    JS_SHOW = """
            divs = document.querySelectorAll("div");
            for (var i = 0, len = divs.length; i < len; i++) {{
                div = divs[i];
                if (div.innerHTML.includes("{0}")) {{
                    div.hidden = false;
                }}
            }};
            """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Live Filter")
        # self.setWindowTitle(config.thisTranslation["liveFilter"])
        self.setMinimumSize(500, 400)
        self.selectedFilter = None
        self.settingBibles = False
        self.filters = [("Pronouns", "he, him, we"), ("Jesus", "Jesus"), ("God", "God")]
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel("Live Filter")
        # title = QLabel(config.thisTranslation["liveFilter"])
        mainLayout.addWidget(title)

        self.filtersTable = QTableView()
        self.filtersTable.setEnabled(True)
        self.filtersTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.filtersTable.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.filtersTable)
        self.filtersTable.setModel(self.dataViewModel)
        self.dataViewModel.itemChanged.connect(self.filterSelectionChanged)
        mainLayout.addWidget(self.filtersTable)

        self.dataViewModel.clear()
        rowCount = 0
        for bible, description in self.filters:
            item = QStandardItem(bible)
            item.setToolTip(bible)
            item.setCheckable(True)
            self.dataViewModel.setItem(rowCount, 0, item)
            item = QStandardItem(description)
            self.dataViewModel.setItem(rowCount, 1, item)
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels(["Filter", config.thisTranslation["description"]])
        # self.dataViewModel.setHorizontalHeaderLabels([config.thisTranslation["filter"], config.thisTranslation["description"]])
        self.filtersTable.resizeColumnsToContents()

        buttonsLayout = QHBoxLayout()
        addButton = QPushButton(config.thisTranslation["add"])
        addButton.clicked.connect(self.addNewFilter)
        buttonsLayout.addWidget(addButton)
        removeButton = QPushButton(config.thisTranslation["remove"])
        removeButton.clicked.connect(self.removeFilter)
        buttonsLayout.addWidget(removeButton)
        renameButton = QPushButton(config.thisTranslation["rename"])
        renameButton.clicked.connect(self.renameFilter)
        buttonsLayout.addWidget(renameButton)
        buttonsLayout.addStretch()
        mainLayout.addLayout(buttonsLayout)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)


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
            for index in range(self.dataViewModel.rowCount()):
                item = self.dataViewModel.item(index)
                if item.checkState() == Qt.Checked:
                    wordSet = self.filters[index][1]
                    words = wordSet.split(",")
                    for word in words:
                        text = word.strip()
                        config.mainWindow.studyPage.runJavaScript(self.JS_SHOW.format(text))
        except Exception as e:
            print(str(e))

    def addNewFilter(self):
        name, ok = QInputDialog.getText(self, 'Filter', 'Filter name:')
        if ok and len(name) > 0 and name != "All":
            pass
            # config.bibleFilters[name] = {}
            # self.showListOfFilters()
            # self.filtersTable.setEnabled(False)

    def removeFilter(self):
        pass
        # config.bibleFilters.pop(self.selectedFilter, None)
        # self.showListOfFilters()
        # self.filtersTable.setEnabled(False)

    def renameFilter(self):
        name, ok = QInputDialog.getText(self, 'Filter', 'Filter name:', text=self.selectedFilter)
        if ok and len(name) > 0 and name != "All":
            pass
            # biblesInFilter = config.bibleFilters[self.selectedFilter]
            # config.bibleFilters.pop(self.selectedFilter, None)
            # self.selectedFilter = name
            # config.bibleFilters[name] = biblesInFilter
            # self.showListOfFilters()
            # self.filtersTable.setEnabled(False)

        # if not self.settingBibles:
        #     if self.selectedFilter is not None:
        #         text = item.text()
        #         biblesInFilter = config.bibleFilters[self.selectedFilter]
        #         if len(biblesInFilter) == 0:
        #             biblesInFilter = []
        #         if text in biblesInFilter:
        #             biblesInFilter.remove(text)
        #         else:
        #             biblesInFilter.append(text)
        #         config.bibleFilters[self.selectedFilter] = biblesInFilter


class Dummy:
    def __init__(self):
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