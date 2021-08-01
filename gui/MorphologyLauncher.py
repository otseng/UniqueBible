import config

if __name__ == "__main__":
    config.noQt = False

from qtpy.QtWidgets import QPushButton
from qtpy.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QLineEdit, QRadioButton, QCheckBox
from db.BiblesSqlite import MorphologySqlite


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
        subLayout = QHBoxLayout()
        subLayout.addWidget(self.searchFieldWidget())
        button = QPushButton("Search")
        button.clicked.connect(self.searchMorphology)
        subLayout.addWidget(button)
        mainLayout.addLayout(subLayout)

        subLayout = QHBoxLayout()
        self.searchTypeBox = QGroupBox("Type")
        layout = QVBoxLayout()
        self.strongsRadioButton = QRadioButton("Strongs")
        self.strongsRadioButton.setToolTip("G80")
        layout.addWidget(self.strongsRadioButton)
        radioButton = QRadioButton("Stem")
        radioButton.setToolTip("ἀδελφοὺς")
        layout.addWidget(radioButton)
        radioButton = QRadioButton("Morphology code")
        radioButton.setToolTip("N-APM")
        layout.addWidget(radioButton)
        radioButton = QRadioButton("Transliteration")
        radioButton.setToolTip("adelphous")
        layout.addWidget(radioButton)
        radioButton = QRadioButton("Gloss")
        radioButton.setToolTip("brother")
        layout.addWidget(radioButton)
        self.searchTypeBox.setLayout(layout)
        subLayout.addWidget(self.searchTypeBox)

        self.partOfSpeechBox = QGroupBox("Part of speech")
        layout = QVBoxLayout()
        self.nounRadioButton = QRadioButton("Noun")
        self.nounRadioButton.toggled.connect(lambda checked, mode="Noun": self.searchModeChanged(checked, mode))
        layout.addWidget(self.nounRadioButton)
        radioButton = QRadioButton("Verb")
        radioButton.toggled.connect(lambda checked, mode="Verb": self.searchModeChanged(checked, mode))
        layout.addWidget(radioButton)
        radioButton = QRadioButton("Conjuction")
        radioButton.toggled.connect(lambda checked, mode="CONJ": self.searchModeChanged(checked, mode))
        layout.addWidget(radioButton)
        self.partOfSpeechBox.setLayout(layout)
        subLayout.addWidget(self.partOfSpeechBox)

        self.genderBox = QGroupBox("Gender")
        self.genderBox.hide()
        layout = QVBoxLayout()
        checkbox = QCheckBox("Masculine")
        layout.addWidget(checkbox)
        checkbox = QCheckBox("Feminine")
        layout.addWidget(checkbox)
        checkbox = QCheckBox("Neuter")
        layout.addWidget(checkbox)
        self.genderBox.setLayout(layout)
        subLayout.addWidget(self.genderBox)

        self.tenseBox = QGroupBox("Tense")
        self.tenseBox.hide()
        layout = QVBoxLayout()
        checkbox = QCheckBox("Present")
        layout.addWidget(checkbox)
        checkbox = QCheckBox("Perfect")
        layout.addWidget(checkbox)
        checkbox = QCheckBox("Imperfect")
        layout.addWidget(checkbox)
        self.tenseBox.setLayout(layout)
        subLayout.addWidget(self.tenseBox)

        self.numberBox = QGroupBox("Number")
        self.numberBox.hide()
        layout = QVBoxLayout()
        checkbox = QCheckBox("Singular")
        layout.addWidget(checkbox)
        checkbox = QCheckBox("Plural")
        layout.addWidget(checkbox)
        self.numberBox.setLayout(layout)
        subLayout.addWidget(self.numberBox)

        mainLayout.addLayout(subLayout)

        self.setLayout(mainLayout)

        self.strongsRadioButton.setChecked(True)
        self.nounRadioButton.setChecked(True)

    def searchModeChanged(self, checked, mode):
        if checked:
            self.mode = mode
            if mode == "Noun":
                self.genderBox.show()
                self.numberBox.show()
                self.tenseBox.hide()
            elif mode == "Verb":
                self.genderBox.show()
                self.numberBox.show()
                self.tenseBox.show()

    def searchFieldWidget(self):
        self.searchField = QLineEdit()
        self.searchField.setText("G2424")
        self.searchField.setClearButtonEnabled(True)
        self.searchField.setToolTip(config.thisTranslation["menu5_searchItems"])
        # self.searchField.returnPressed.connect(self.searchBible)
        return self.searchField

    def searchMorphology(self):
        morphology = MorphologySqlite()
        verses = morphology.searchByLexicalAndMorphology(1, 66, self.searchField.text(), self.mode)
        print(len(verses))


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

