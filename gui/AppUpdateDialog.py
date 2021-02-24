import sys
import config

from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton, QLineEdit, \
    QHBoxLayout
from util.DateUtil import DateUtil
from util.LanguageUtil import LanguageUtil
from util.TextUtil import TextUtil
from util.UpdateUtil import UpdateUtil


class AppUpdateDialog(QDialog):

    def __init__(self, parent):
        super(AppUpdateDialog, self).__init__()

        self.parent = parent
        self.setWindowTitle("UBA Update")
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
        self.updateNowButton.setEnabled(True)
        self.updateNowButton.clicked.connect(self.updateNow)
        if self.uptodate:
            ubaUptodate = QLabel("UBA is up-to-date")
            ubaUptodate.setStyleSheet("color: rgb(128, 255, 7);")
            self.layout.addWidget(ubaUptodate)
        else:
            self.layout.addWidget(self.updateNowButton)

        self.layout.addWidget(QLabel("Last check: {0}".format(
            DateUtil.formattedLocalDate(UpdateUtil.lastAppUpdateCheckDateObject()))))
        self.layout.addWidget(QLabel("Next check: {0}".format(
            DateUtil.formattedLocalDate(
                DateUtil.addDays(UpdateUtil.lastAppUpdateCheckDateObject(), int(config.daysElapseForNextAppUpdateCheck)
                )))))

        row = QHBoxLayout()
        row.addWidget(QLabel("Days between checks:"))
        self.daysInput = QLineEdit()
        self.daysInput.setText(str(config.daysElapseForNextAppUpdateCheck))
        self.daysInput.setMaxLength(3)
        self.daysInput.setMaximumWidth(40)
        row.addWidget(self.daysInput)
        self.layout.addLayout(row)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.setDaysElapse)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.updateNowButton.setFocus()

        if self.uptodate:
            self.daysInput.setFocus()
        else:
            self.setTabOrder(self.updateNowButton, self.daysInput)
            self.setTabOrder(self.daysInput, self.updateNowButton)
            self.updateNowButton.setFocus()

    def updateNow(self):
        debug = True
        self.updateNowButton.setText("Updating...")
        self.updateNowButton.setEnabled(False)
        UpdateUtil.updateUniqueBibleApp(self.parent, debug)
        self.updateNowButton.setText("Done!")

    def setDaysElapse(self):
        config.daysElapseForNextAppUpdateCheck = TextUtil.getDigits(self.daysInput.text())


if __name__ == '__main__':
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    app = QApplication(sys.argv)
    window = AppUpdateDialog(None)
    window.exec_()