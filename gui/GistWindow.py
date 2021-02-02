import sys

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QCheckBox, QLabel, QLineEdit, \
    QPushButton, QHBoxLayout


class GistWindow(QDialog):

    def __init__(self, enable, token):
        super(GistWindow, self).__init__()

        self.enable = enable
        self.token = token

        self.setWindowTitle("Gist")
        self.setMinimumWidth(380)
        self.layout = QVBoxLayout()

        self.testStatus = QLabel("")
        self.layout.addWidget(self.testStatus)

        self.enableGist = QCheckBox("Enable Gist")
        self.enableGist.setChecked(enable)
        self.enableGist.stateChanged.connect(self.enableButtons)
        self.layout.addWidget(self.enableGist)

        self.layout.addWidget(QLabel("Gist Token"))
        self.gistToken = QLineEdit()
        self.gistToken.setText(token)
        self.gistToken.setMinimumWidth(80)
        self.gistToken.textChanged.connect(self.enableButtons)
        self.layout.addWidget(self.gistToken)

        self.testButton = QPushButton("Test Connection")
        self.testButton.setEnabled(False)
        self.testButton.clicked.connect(self.checkStatus)
        self.layout.addWidget(self.testButton)

        actionLayout = QHBoxLayout()
        self.uploadButton = QPushButton("Upload to Gist")
        self.uploadButton.setEnabled(False)
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

        self.checkStatus()

    def enableButtons(self):
        if self.enableGist.isChecked() and len(self.gistToken.text()) >= 40:
            self.testButton.setEnabled(True)
        else:
            self.testButton.setEnabled(False)

    def checkStatus(self):
        if not self.enableGist or len(self.gistToken.text()) < 40:
            self.setStatus("Not connected", False)
        else:
            self.setStatus("Maybe", True)

    def setStatus(self, message, connected):
        self.testStatus.setText("Status: " + message)
        if connected:
            self.testStatus.setStyleSheet("color: rgb(128, 255, 7);")
        else:
            self.testStatus.setStyleSheet("color: rgb(253, 128, 8);")

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    gistWindow = GistWindow(False, "abc")
    if gistWindow.exec_():
        print(gistWindow.gistToken.text())
        print(gistWindow.enableGist.isChecked())
    else:
        print("Cancel")