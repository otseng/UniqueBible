import config
import sys
from qtpy.QtWidgets import QWidget, QApplication, QRadioButton, QVBoxLayout


class ConfigurePresentationWindow(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle("Configure Presentation")
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()

    def setupVariables(self):
        pass

    def setupUI(self):

        from qtpy.QtCore import Qt
        from qtpy.QtWidgets import QHBoxLayout, QFormLayout, QSlider, QPushButton, QPlainTextEdit, QCheckBox, QComboBox

        layout = QHBoxLayout()

        layout1 = QFormLayout()

        self.fontsizeslider = QSlider(Qt.Horizontal)
        self.fontsizeslider.setMinimum(1)
        self.fontsizeslider.setMaximum(12)
        self.fontsizeslider.setTickInterval(2)
        self.fontsizeslider.setSingleStep(2)
        self.fontsizeslider.setValue(config.presentationFontSize / 0.5)
        self.fontsizeslider.setToolTip(str(config.presentationFontSize))
        self.fontsizeslider.valueChanged.connect(self.presentationFontSizeChanged)
        layout1.addRow("Font Size", self.fontsizeslider)

        self.changecolorbutton = QPushButton()
        buttonStyle = "QPushButton {0}background-color: {2}; color: {3};{1}".format("{", "}", config.presentationColorOnDarkTheme if config.theme == "dark" else config.presentationColorOnLightTheme, "white" if config.theme == "dark" else "black")
        self.changecolorbutton.setStyleSheet(buttonStyle)
        self.changecolorbutton.setToolTip("Change Color")
        self.changecolorbutton.clicked.connect(self.changeColor)
        layout1.addRow("Font Color", self.changecolorbutton)

        self.marginslider = QSlider(Qt.Horizontal)
        self.marginslider.setMinimum(0)
        self.marginslider.setMaximum(200)
        self.marginslider.setTickInterval(50)
        self.marginslider.setSingleStep(50)
        self.marginslider.setValue(config.presentationMargin)
        self.marginslider.setToolTip(str(config.presentationMargin))
        self.marginslider.valueChanged.connect(self.presentationMarginChanged)
        layout1.addRow("Margin", self.marginslider)

        self.verticalpositionslider = QSlider(Qt.Horizontal)
        self.verticalpositionslider.setMinimum(10)
        self.verticalpositionslider.setMaximum(90)
        self.verticalpositionslider.setTickInterval(10)
        self.verticalpositionslider.setSingleStep(10)
        self.verticalpositionslider.setValue(config.presentationVerticalPosition)
        self.verticalpositionslider.setToolTip(str(config.presentationVerticalPosition))
        self.verticalpositionslider.valueChanged.connect(self.presentationVerticalPositionChanged)
        layout1.addRow("Vertical Position", self.verticalpositionslider)

        self.horizontalpositionslider = QSlider(Qt.Horizontal)
        self.horizontalpositionslider.setMinimum(10)
        self.horizontalpositionslider.setMaximum(90)
        self.horizontalpositionslider.setTickInterval(10)
        self.horizontalpositionslider.setSingleStep(10)
        self.horizontalpositionslider.setValue(config.presentationHorizontalPosition)
        self.horizontalpositionslider.setToolTip(str(config.presentationHorizontalPosition))
        self.horizontalpositionslider.valueChanged.connect(self.presentationHorizontalPositionChanged)
        layout1.addRow("Horizontal Position", self.horizontalpositionslider)

        self.showBibleSelection = QRadioButton()
        self.showBibleSelection.setChecked(True)
        self.showBibleSelection.clicked.connect(lambda: self.selectRadio("bible"))
        layout1.addRow("Bible", self.showBibleSelection)

        self.showHymnsSelection = QRadioButton()
        self.showHymnsSelection.setChecked(False)
        self.showHymnsSelection.clicked.connect(lambda: self.selectRadio("hymns"))
        layout1.addRow("Hymns", self.showHymnsSelection)

        # Second column

        layout2 = QVBoxLayout()

        self.bibleWidget = QWidget()
        self.bibleLayout = QFormLayout()

        checkbox = QCheckBox()
        checkbox.setText("")
        checkbox.setChecked(config.presentationParser)
        checkbox.stateChanged.connect(self.presentationParserChanged)
        checkbox.setToolTip("Parse bible verse reference in the entered text")
        self.bibleLayout.addRow("Bible Reference", checkbox)

        versionCombo = QComboBox()
        self.bibleVersions = self.parent.textList
        versionCombo.addItems(self.bibleVersions)
        initialIndex = 0
        if config.mainText in self.bibleVersions:
            initialIndex = self.bibleVersions.index(config.mainText)
        versionCombo.setCurrentIndex(initialIndex)
        versionCombo.currentIndexChanged.connect(self.changeBibleVersion)
        self.bibleLayout.addRow("Bible Version", versionCombo)

        self.textEntry = QPlainTextEdit("John 3:16; Rm 5:8")
        self.bibleLayout.addWidget(self.textEntry)

        self.bibleWidget.setLayout(self.bibleLayout)

        self.hymnWidget = QWidget()
        self.hymnLayout = QFormLayout()

        checkbox = QCheckBox()
        checkbox.setText("")
        checkbox.setChecked(config.presentationParser)
        checkbox.stateChanged.connect(self.presentationParserChanged)
        self.hymnLayout.addRow("Hymn", checkbox)

        self.hymnWidget.setLayout(self.hymnLayout)

        layout2.addWidget(self.bibleWidget)
        layout2.addWidget(self.hymnWidget)

        button = QPushButton("Presentation")
        button.setToolTip("Go to Presentation")
        button.clicked.connect(self.goToPresentation)
        layout2.addWidget(button)

        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)

        self.hymnWidget.hide()

    def selectRadio(self, option):
        if option == "bible":
            self.bibleWidget.show()
            self.hymnWidget.hide()
        elif option == "hymns":
            self.bibleWidget.hide()
            self.hymnWidget.show()

    def goToPresentation(self):
        command = "SCREEN:::{0}".format(self.textEntry.toPlainText())
        self.parent.runTextCommand(command)

    def changeColor(self):

        from qtpy.QtGui import QColor
        from qtpy.QtWidgets import QColorDialog

        color = QColorDialog.getColor(QColor(config.presentationColorOnDarkTheme if config.theme == "dark" else config.presentationColorOnLightTheme), self)
        if color.isValid():
            colorName = color.name()
            if config.theme == "dark":
                config.presentationColorOnDarkTheme = colorName
            else:
                config.presentationColorOnLightTheme = colorName
            buttonStyle = "QPushButton {0}background-color: {2}; color: {3};{1}".format("{", "}", colorName, "white" if config.theme == "dark" else "black")
            self.changecolorbutton.setStyleSheet(buttonStyle)

    def presentationFontSizeChanged(self, value):
        config.presentationFontSize = value * 0.5
        self.fontsizeslider.setToolTip(str(config.presentationFontSize))

    def presentationMarginChanged(self, value):
        config.presentationMargin = value
        self.marginslider.setToolTip(str(config.presentationMargin))

    def presentationVerticalPositionChanged(self, value):
        config.presentationVerticalPosition = value
        self.verticalpositionslider.setToolTip(str(config.presentationVerticalPosition))
    
    def presentationHorizontalPositionChanged(self, value):
        config.presentationHorizontalPosition = value
        self.horizontalpositionslider.setValue(config.presentationHorizontalPosition)

    def presentationParserChanged(self):
        config.presentationParser = not config.presentationParser

    def changeBibleVersion(self, index):
        if __name__ == '__main__':
            config.mainText = self.bibleVersions[index]
        else:
            command = "TEXT:::{0}".format(self.bibleVersions[index])
            self.parent.runTextCommand(command)


if __name__ == '__main__':
    import checkup
    from util.ConfigUtil import ConfigUtil
    ConfigUtil.setup()
    config.activeVerseNoColour = "white"
    from gui.MainWindow import MainWindow
    app = QApplication(sys.argv)
    config.mainWindow = MainWindow()
    config.presentationParser = True
    from plugins.startup.screenCommand import presentReferenceOnFullScreen
    config.mainWindow.textCommandParser.interpreters["screen"] = (presentReferenceOnFullScreen, "")

config.mainWindow.configurePresentationWindow = ConfigurePresentationWindow(config.mainWindow)
config.mainWindow.configurePresentationWindow.show()

if __name__ == '__main__':
    sys.exit(app.exec_())