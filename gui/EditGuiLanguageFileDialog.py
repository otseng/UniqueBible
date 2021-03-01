import operator
import sys

from PySide2.QtCore import QAbstractTableModel, Qt, SIGNAL
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QTableView, QInputDialog, QLineEdit, \
    QHBoxLayout
from Languages import Languages


class EditGuiLanguageFileDialog(QDialog):

    def __init__(self, language):
        super(EditGuiLanguageFileDialog, self).__init__()

        self.language = language
        langDefinition = LanguageUtil.loadTranslation(language)
        self.languages = []
        for key in langDefinition.keys():
            self.languages.append([key, langDefinition[key]])

        self.setWindowTitle("Edit GUI Language File")
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        self.layout = QVBoxLayout()

        row = QHBoxLayout()
        self.filterEntry1 = QLineEdit()
        self.filterEntry1.textChanged.connect(self.filterChanged1)
        row.addWidget(self.filterEntry1)
        self.filterEntry2 = QLineEdit()
        self.filterEntry2.textChanged.connect(self.filterChanged2)
        row.addWidget(self.filterEntry2)
        self.layout.addLayout(row)

        self.table = QTableView()
        self.model = DisplayLanguagesModel(self, self.languages)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.clickedRow)
        self.layout.addWidget(self.table)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def clickedRow(self, index):
        row = self.model.getRow(index.row())
        (action, key) = row
        newKey, ok = QInputDialog.getText(self, 'Shortcut', action, QLineEdit.Normal, key)
        if ok:
            self.model.list[index.row()] = (action, newKey)
            for item in self.model.fullList:
                if item[0] == action:
                    item[1] = newKey

    def save(self):
        print("Save it")

    def filterChanged1(self, text):
        self.model.filter(0, text)

    def filterChanged2(self, text):
        self.model.filter(1, text)

class DisplayLanguagesModel(QAbstractTableModel):

    def __init__(self, parent, data, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.fullList = data
        self.list = data
        self.header = ['key', Languages.decode(parent.language)]
        self.col = 0
        self.order = None

    def filter(self, col, text):
        newList = []
        for item in self.fullList:
            if text.lower() in item[col].lower():
                newList.append(item)
        self.list = newList
        self.sort(self.col, self.order)

    def rowCount(self, parent):
        return len(self.list)

    def columnCount(self, parent):
        if len(self.list) == 0:
            return 0
        else:
            return len(self.list[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.list[index.row()][index.column()]

    def getRow(self, row):
        return self.list[row]

    def setRow(self, row, data):
        self.list[row] = data

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.col = col
        self.order = order
        self.list = sorted(self.list, key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.list.reverse()
        self.emit(SIGNAL("layoutChanged()"))

if __name__ == '__main__':
    from util.LanguageUtil import LanguageUtil

    LanguageUtil.loadTranslation("en_US")
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = EditGuiLanguageFileDialog("en_US")
    window.exec_()
    window.close()