import config
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
from qtpy.QtWidgets import QInputDialog
from qtpy.QtWidgets import QRadioButton
from qtpy.QtWidgets import QListWidget


class DownloadBibleMp3Dialog(QDialog):

    bibles = {
        "KJV": "otseng/UniqueBible_MP3_KJV"
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["gitHubBibleMp3Files"])
        self.setMinimumSize(680, 500)
        self.selectedBible = None
        self.settingBibles = False
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["gitHubBibleMp3Files"])
        mainLayout.addWidget(title)

        self.versionsLayout = QVBoxLayout()
        self.versionsList = QListWidget()
        self.versionsList.itemClicked.connect(self.selectBible)
        self.versionsList.addItem("KJV")
        self.versionsList.setMaximumHeight(50)
        self.versionsLayout.addWidget(self.versionsList)
        mainLayout.addLayout(self.versionsLayout)

        self.downloadTable = QTableView()
        self.downloadTable.setEnabled(False)
        self.downloadTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.downloadTable.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.downloadTable)
        self.downloadTable.setModel(self.dataViewModel)
        mainLayout.addWidget(self.downloadTable)

        buttonsLayout = QHBoxLayout()
        downloadButton = QPushButton(config.thisTranslation["download"])
        downloadButton.clicked.connect(self.download)
        buttonsLayout.addWidget(downloadButton)
        selectAllButton = QPushButton(config.thisTranslation["selectAll"])
        selectAllButton.clicked.connect(self.selectAll)
        buttonsLayout.addWidget(selectAllButton)
        selectNoneButton = QPushButton(config.thisTranslation["selectNone"])
        selectNoneButton.clicked.connect(self.selectNone)
        buttonsLayout.addWidget(selectNoneButton)
        buttonsLayout.addStretch()
        mainLayout.addLayout(buttonsLayout)

        buttonLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["close"])
        button.clicked.connect(self.close)
        buttonLayout.addWidget(button)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def selectBible(self, item):
        from util.GithubUtil import GithubUtil

        self.selectedBible = item.text()
        self.downloadTable.setEnabled(True)

        repo = DownloadBibleMp3Dialog.bibles[self.selectedBible]
        github = GithubUtil(repo)
        repoData = github.getRepoData()
        self.settingBibles = True
        self.dataViewModel.clear()
        rowCount = 0
        for file in repoData.keys():
            item = QStandardItem(file)
            item.setCheckable(True)
            # if file in biblesInCollection:
            #     item.setCheckState(Qt.Checked)
            self.dataViewModel.setItem(rowCount, 0, item)
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels(
            [config.thisTranslation["menu_book"]])
        self.downloadTable.resizeColumnsToContents()
        self.settingBibles = False

    def selectAll(self):
        name, ok = QInputDialog.getText(self, 'Collection', 'Collection name:')
        if ok and len(name) > 0 and name != "All":
            config.bibleCollections[name] = {}
            self.showListOfCollections()
            self.downloadTable.setEnabled(False)

    def selectNone(self):
        config.bibleCollections.pop(self.selectedBible, None)
        self.showListOfCollections()
        self.downloadTable.setEnabled(False)

    def download(self):
        name, ok = QInputDialog.getText(self, 'Collection', 'Collection name:', text=self.selectedBible)
        if ok and len(name) > 0 and name != "All":
            biblesInCollection = config.bibleCollections[self.selectedBible]
            config.bibleCollections.pop(self.selectedBible, None)
            self.selectedBible = name
            config.bibleCollections[name] = biblesInCollection
            self.showListOfCollections()
            self.downloadTable.setEnabled(False)


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
    dialog = DownloadBibleMp3Dialog()
    dialog.exec_()