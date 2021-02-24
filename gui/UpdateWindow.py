import sys

import config

from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton
from util.LanguageUtil import LanguageUtil
from util.UpdateUtil import UpdateUtil


class UpdateWindow(QDialog):

    def __init__(self):
        super(UpdateWindow, self).__init__()

        self.setWindowTitle("UBA Update")
        # self.setMinimumWidth(250)
        self.layout = QVBoxLayout()

        self.latestVersion = UpdateUtil.getLatestVersion()
        self.currentVersion = UpdateUtil.getCurrentVersion()

        if UpdateUtil.currentIsLatest(self.currentVersion, self.latestVersion):
            self.uptodate = True
        else:
            self.uptodate = False

        if not self.uptodate:
            self.layout.addWidget(QLabel("Latest version: {0}".format(self.latestVersion)))
        self.layout.addWidget(QLabel("Current version: {0}".format(self.currentVersion)))

        self.updateNowButton = QPushButton("Update now")
        self.updateNowButton.setEnabled(False)
        self.updateNowButton.clicked.connect(self.updateNow)
        if self.uptodate:
            self.layout.addWidget(QLabel("UBA is up-to-date"))
        else:
            self.layout.addWidget(self.updateNowButton)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.enableButtons()

    def enableButtons(self):
        if UpdateUtil.currentIsLatest(self.currentVersion, self.latestVersion):
            self.updateNowButton.setEnabled(False)
        else:
            self.updateNowButton.setEnabled(True)

    def updateNow(self):
        pass


if __name__ == '__main__':
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    app = QApplication(sys.argv)
    window = UpdateWindow()
    window.exec_()