import config
from qtpy.QtGui import QKeySequence
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QAction
from qtpy.QtWebEngineWidgets import QWebEngineView

class WebEngineViewPopover(QWebEngineView):

    def __init__(self, parent, name, source):
        super().__init__()
        self.parent = parent
        self.name = name
        self.source = source
        self.setWindowTitle("Unique Bible App")
        self.titleChanged.connect(self.popoverTextCommandChanged)
        self.page().loadFinished.connect(self.finishViewLoading)

        # add context menu (triggered by right-clicking)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.addMenuActions()

    def finishViewLoading(self):
        # scroll to the study verse
        self.page().runJavaScript("var activeVerse = document.getElementById('v"+str(config.studyB)+"."+str(config.studyC)+"."+str(config.studyV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = 'red'; } else if (document.getElementById('v0.0.0') != null) { document.getElementById('v0.0.0').scrollIntoView(); }")

    def popoverTextCommandChanged(self, newTextCommand):
        # reset document.title
        changeTitle = "document.title = 'UniqueBible.app';"
        self.page().runJavaScript(changeTitle)
        # run textCommandChanged from parent
        self.parent.parent.parent.textCommandChanged(newTextCommand, self.source)

    def addMenuActions(self):
        copyText = QAction(self)
        copyText.setText(config.thisTranslation["context1_copy"])
        copyText.triggered.connect(self.copySelectedText)
        self.addAction(copyText)

        runAsCommandLine = QAction(self)
        runAsCommandLine.setText(config.thisTranslation["context1_command"])
        runAsCommandLine.triggered.connect(self.runAsCommand)
        self.addAction(runAsCommandLine)

        if hasattr(config, "macroIsRunning") and config.macroIsRunning:
            spaceBar = QAction(self)
            spaceBar.setShortcut(QKeySequence(" "))
            spaceBar.triggered.connect(self.spaceBarPressed)
            self.addAction(spaceBar)
    
        escKey = QAction(self)
        escKey.setShortcut(QKeySequence(Qt.Key_Escape))
        escKey.triggered.connect(self.escKeyPressed)
        self.addAction(escKey)

        qKey = QAction(self)
        qKey.setShortcut(QKeySequence(Qt.Key_Q))
        qKey.triggered.connect(self.escKeyPressed)
        self.addAction(qKey)

    def messageNoSelection(self):
        self.parent.displayMessage("{0}\n{1}".format(config.thisTranslation["message_run"], config.thisTranslation["selectTextFirst"]))

    def copySelectedText(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            self.page().triggerAction(self.page().Copy)

    def runAsCommand(self):
        selectedText = self.selectedText()
        self.parent.parent.parent.textCommandChanged(selectedText, "main")

    def closeEvent(self, event):
        if hasattr(config, "macroIsRunning") and config.macroIsRunning:
            config.pauseMode = False

    def spaceBarPressed(self):
        if hasattr(config, "macroIsRunning") and config.macroIsRunning:
            config.pauseMode = False

    def escKeyPressed(self):
        if hasattr(config, "macroIsRunning") and config.macroIsRunning:
            config.quitMacro = True
            config.pauseMode = False
        self.close()

