import sys
import webbrowser
import config

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPlainTextEdit


class AboutDialog(QDialog):

    def __init__(self):
        super(AboutDialog, self).__init__()

        self.wikiLink = "https://github.com/eliranwong/UniqueBible/wiki"

        self.setWindowTitle(config.thisTranslation["menu_about"])
        self.layout = QVBoxLayout()

        self.appName = QLabel("Unique Bible App")
        self.appName.mouseReleaseEvent = self.openWiki
        self.layout.addWidget(self.appName)
        self.layout.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["version"], config.version)))

        with open("latest_changes.txt", "r", encoding="utf-8") as fileObject:
            text = fileObject.read()

        self.layout.addWidget(QLabel("{0}}:".format(config.thisTranslation["latest_changes"])))
        self.latestChanges = QPlainTextEdit()
        self.latestChanges.setPlainText(text)
        self.latestChanges.setReadOnly(True)
        self.layout.addWidget(self.latestChanges)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def openWiki(self, event):
        webbrowser.open(self.wikiLink)


if __name__ == '__main__':
    from util.ConfigUtil import ConfigUtil

    ConfigUtil.setup()
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = AboutDialog()
    window.exec_()
    window.close()