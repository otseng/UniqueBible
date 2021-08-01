import config
from gui.CheckableComboBox import CheckableComboBox
from qtpy.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QLineEdit, QRadioButton, QCheckBox

class MorphologyLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["message_searchMorphology"])
        # set up variables
        self.parent = parent
        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.searchFieldWidget())
        subLayout = QHBoxLayout()
        partOfSeechBox = QGroupBox("Part of speech")
        partOfSeechLayout = QVBoxLayout()
        radioButton = QRadioButton("Noun")
        radioButton.toggled.connect(lambda checked, mode="noun": self.searchModeChanged(checked, mode))
        partOfSeechLayout.addWidget(radioButton)
        radioButton = QRadioButton("Verb")
        radioButton.toggled.connect(lambda checked, mode="verb": self.searchModeChanged(checked, mode))
        partOfSeechLayout.addWidget(radioButton)
        radioButton = QRadioButton("Adjective")
        radioButton.toggled.connect(lambda checked, mode="adjective": self.searchModeChanged(checked, mode))
        partOfSeechLayout.addWidget(radioButton)
        partOfSeechBox.setLayout(partOfSeechLayout)
        subLayout.addWidget(partOfSeechBox)
        mainLayout.addLayout(subLayout)
        self.setLayout(mainLayout)

    def searchFieldWidget(self):
        self.searchField = QLineEdit()
        self.searchField.setClearButtonEnabled(True)
        self.searchField.setToolTip(config.thisTranslation["menu5_searchItems"])
        # self.searchField.returnPressed.connect(self.searchBible)
        return self.searchField

    def searchModeChanged(self, checked, mode):
        if checked:
            print(mode)

## Standalone development code

class DummyParent():
    def runTextCommand(self, command):
        print(command)

    def verseReference(self, command):
        return ['', '']


if __name__ == "__main__":
    from qtpy import QtWidgets
    from qtpy.QtWidgets import QWidget
    import sys

    from util.LanguageUtil import LanguageUtil
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    app = QtWidgets.QApplication(sys.argv)
    window = MorphologyLauncher(DummyParent())
    window.show()
    sys.exit(app.exec_())

