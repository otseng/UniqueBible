import glob
import sys
import config

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, \
    QComboBox


class ModifyDatabaseDialog(QDialog):

    def __init__(self, filetype, filename):
        super().__init__()

        from BiblesSqlite import Bible

        self.filetype = filetype
        self.filename = filename

        self.setWindowTitle("Update Database")
        self.layout = QVBoxLayout()
        self.setMinimumWidth(300)

        if filetype == "bible":
            bible = Bible(filename)
            if not bible.checkColumnExists("Details", "Language"):
                bible.addColumnToTable("Details", "Language", "NVARCHAR(10)")
            if not bible.checkColumnExists("Details", "Font"):
                bible.addColumnToTable("Details", "Font", "TEXT")

            row = QHBoxLayout()
            row.addWidget(QLabel("Title: "))
            self.bibleTitle = QLineEdit()
            self.bibleTitle.setText(bible.bibleInfo())
            row.addWidget(self.bibleTitle)
            self.layout.addLayout(row)

            row = QHBoxLayout()
            row.addWidget(QLabel("Language: "))
            self.bibleLanguage = QLineEdit()
            self.bibleLanguage.setText(bible.getLanguage())
            row.addWidget(self.bibleLanguage)
            self.layout.addLayout(row)

            fonts = [''] + sorted(glob.glob("htmlResources/fonts/*.ttf"))
            try:
                index = fonts.index(bible.getFont())
            except:
                index = 0
            row = QHBoxLayout()
            row.addWidget(QLabel("Font: "))
            self.fontList = QComboBox()
            self.fontList.addItems(fonts)
            self.fontList.setCurrentIndex(index)
            row.addWidget(self.fontList)
            self.layout.addLayout(row)
        else:
            self.layout.addWidget(QLabel("{0} is not supported".format(filetype)))

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


if __name__ == '__main__':
    from util.ConfigUtil import ConfigUtil
    from util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")

    config.mainText = "KJV"
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = ModifyDatabaseDialog("bible", config.mainText)
    window.exec_()
    window.close()