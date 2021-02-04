import sys
import config

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QCheckBox, QLabel, QLineEdit, \
    QPushButton, QHBoxLayout

from util.GitHubGist import GitHubGist
from util.NoteService import NoteService


class GistWindow(QDialog):

    def __init__(self):
        super(GistWindow, self).__init__()

        self.gistToken = config.gistToken
        self.connected = False

        self.setWindowTitle("Gist")
        self.setMinimumWidth(380)
        self.layout = QVBoxLayout()

        self.testStatus = QLabel("")
        self.layout.addWidget(self.testStatus)

        self.layout.addWidget(QLabel("Gist Token"))
        self.gistTokenInput = QLineEdit()
        self.gistTokenInput.setText(self.gistToken)
        self.gistTokenInput.setMaxLength(40)
        self.gistTokenInput.textChanged.connect(self.enableButtons)
        self.layout.addWidget(self.gistTokenInput)

        self.testButton = QPushButton("Test Connection")
        self.testButton.setEnabled(False)
        self.testButton.clicked.connect(self.checkStatus)
        self.layout.addWidget(self.testButton)

        actionLayout = QHBoxLayout()
        self.uploadButton = QPushButton("Upload to Gist")
        self.uploadButton.setEnabled(False)
        self.uploadButton.clicked.connect(self.uploadToGist)
        actionLayout.addWidget(self.uploadButton)

        self.downloadButton = QPushButton("Download from Gist")
        self.downloadButton.setEnabled(False)
        actionLayout.addWidget(self.downloadButton)
        self.layout.addLayout(actionLayout)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.enableButtons()
        self.checkStatus()

    def enableButtons(self):
        if len(self.gistTokenInput.text()) >= 40:
            self.testButton.setEnabled(True)
        else:
            self.testButton.setEnabled(False)
            self.connected = False
            self.setStatus("", False)
        if self.connected:
            self.testButton.setEnabled(False)
            self.uploadButton.setEnabled(True)
            self.downloadButton.setEnabled(True)
        else:
            self.uploadButton.setEnabled(False)
            self.downloadButton.setEnabled(False)

    def checkStatus(self):
        if len(self.gistTokenInput.text()) < 40:
            self.setStatus("Not connected", False)
            self.connected = False
        else:
            self.gh = GitHubGist(self.gistTokenInput.text())
            if self.gh.connected:
                self.setStatus("Connected to " + self.gh.user.name, True)
                self.connected = True
            else:
                self.setStatus(self.gh.status, False)
                self.connected = False
        self.enableButtons()

    def setStatus(self, message, connected):
        self.testStatus.setText("Status: " + message)
        if connected:
            self.testStatus.setStyleSheet("color: rgb(128, 255, 7);")
        else:
            self.testStatus.setStyleSheet("color: rgb(253, 128, 8);")

    def uploadToGist(self):
        gh = GitHubGist()
        ns = NoteService.getNoteSqlite()
        count = 0
        notes = ns.getAllChapters()
        for note in notes:
            count += 1
            book = note[0]
            chapter = note[1]
            content = note[2]
            updatedL = note[3]
            gh.open_gist_chapter_note(book, chapter)
            updatedG = gh.get_updated()
            if updatedG == 0:
                gh.update_content(content)
            elif updatedL is not None and updatedL > updatedG:
                gh.update_content(content)
            else:
                gistFile = gh.get_file()
                sizeG = gistFile.size
                sizeL = len(content)
        self.setStatus("Uploaded {0} notes".format(count), True)

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    gistWindow = GistWindow()
    if gistWindow.exec_():
        print(gistWindow.gistTokenInput.text())
    else:
        print("Cancel")