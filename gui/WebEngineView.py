from shutil import copyfile

from util.Languages import Languages
import config, os, platform, webbrowser, re
from functools import partial
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFileDialog
#from qtpy.QtGui import QDesktopServices
#from qtpy.QtGui import QKeySequence
from qtpy.QtGui import QGuiApplication
from qtpy.QtWidgets import QAction, QApplication, QDesktopWidget, QMenu
from qtpy.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineSettings
from util.BibleVerseParser import BibleVerseParser
from db.BiblesSqlite import BiblesSqlite
from util.Translator import Translator
from gui.WebEngineViewPopover import WebEngineViewPopover
from util.FileUtil import FileUtil
from util.TextUtil import TextUtil
from util.BibleBooks import BibleBooks

class WebEngineView(QWebEngineView):
    
    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name
        self.setPage(WebEnginePage(self))
        self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.page().fullScreenRequested.connect(lambda request: request.accept())
       
        # add context menu (triggered by right-clicking)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.selectionChanged.connect(self.updateContextMenu)
        self.addMenuActions()

    def displayMessage(self, message):
        self.parent.parent.displayMessage(message)

    def updateContextMenu(self):
        text = self.getText()
        parser = BibleVerseParser(config.parserStandarisation)
        book = parser.bcvToVerseReference(self.getBook(), 1, 1)[:-4]
        del parser
        self.searchText.setText("{1} {0}".format(text, config.thisTranslation["context1_search"]))
        self.searchTextInBook.setText("{2} {0} > {1}".format(text, book, config.thisTranslation["context1_search"]))
        #self.searchBibleTopic.setText("{1} > {0}".format(config.topic, config.thisTranslation["menu5_topics"]))
        #self.searchBibleDictionary.setText("{1} > {0}".format(config.dictionary, config.thisTranslation["context1_dict"]))
        #self.searchBibleEncyclopedia.setText("{1} > {0}".format(config.encyclopedia, config.thisTranslation["context1_encyclopedia"]))
        #self.searchThirdDictionary.setText("{1} > {0}".format(config.thirdDictionary, config.thisTranslation["menu5_3rdDict"]))

    def getText(self):
        text = {
            "main": config.mainText,
            "study": config.studyText,
            "instant": config.mainText,
        }
        return text[self.name]

    def getBook(self):
        book = {
            "main": config.mainB,
            "study": config.studyB,
            "instant": config.mainB,
        }
        return book[self.name]

    def switchToCli(self):
        if config.isHtmlTextInstalled:
            config.pluginContext = self.name
            QGuiApplication.instance().setApplicationName("UniqueBible.app CLI")
            config.pluginContext = ""
        else:
            self.displayMessage("CLI feature is not enabled! \n Install module 'html-text' first, by running 'pip3 install html-text'!")

    def addMenuActions(self):

        action = QAction(self)
        action.setText(config.thisTranslation["context1_search"])
        action.triggered.connect(self.searchPanel)
        self.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["saveHtml"])
        action.triggered.connect(self.saveHtml)
        self.addAction(action)

        subMenu = QMenu()

        copyText = QAction(self)
        copyText.setText(config.thisTranslation["text"])
        copyText.triggered.connect(self.copySelectedText)
        subMenu.addAction(copyText)

        copyText = QAction(self)
        copyText.setText(config.thisTranslation["textWithReference"])
        copyText.triggered.connect(self.copySelectedTextWithReference)
        subMenu.addAction(copyText)

        copyReferences = QAction(self)
        copyReferences.setText(config.thisTranslation["bibleReferences"])
        copyReferences.triggered.connect(self.copyAllReferences)
        subMenu.addAction(copyReferences)

        copyHtml = QAction(self)
        copyHtml.setText(config.thisTranslation["htmlCode"])
        copyHtml.triggered.connect(self.copyHtmlCode)
        subMenu.addAction(copyHtml)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_copy"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        subMenu = QMenu()

        self.searchText = QAction(self)
        self.searchText.setText("{0} [{1}]".format(config.thisTranslation["context1_search"], config.mainText))
        self.searchText.triggered.connect(self.searchSelectedText)
        subMenu.addAction(self.searchText)

        self.searchTextInBook = QAction(self)
        self.searchTextInBook.setText(config.thisTranslation["context1_current"])
        self.searchTextInBook.triggered.connect(self.searchSelectedTextInBook)
        subMenu.addAction(self.searchTextInBook)

        searchFavouriteBible = QAction(self)
        searchFavouriteBible.setText(config.thisTranslation["context1_favourite"])
        searchFavouriteBible.triggered.connect(self.searchSelectedFavouriteBible)
        subMenu.addAction(searchFavouriteBible)

        action = QAction(self)
        action.setText(config.thisTranslation["cp0"])
        action.setMenu(subMenu)
        self.addAction(action)

        subMenu = QMenu()

        bibleVerseParser = BibleVerseParser(config.parserStandarisation)
        for bookNo in range(1, 67):
            action = QAction(self)
            bookName = bibleVerseParser.standardFullBookName[str(bookNo)]
            action.setText(bookName)
            action.triggered.connect(partial(self.openReferencesInBook, bookName))
            subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["openInBook"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        subMenu = QMenu()

        for text in self.parent.parent.textList:
            action = QAction(self)
            action.setText(text)
            action.triggered.connect(partial(self.openReferenceInBibleVersion, text))
            subMenu.addAction(action)
        
        separator = QAction(self)
        separator.setSeparator(True)
        subMenu.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["all"])
        action.triggered.connect(self.compareAllVersions)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["openReferences"])
        action.setMenu(subMenu)
        self.addAction(action)

        subMenu = QMenu()

        for text in self.parent.parent.textList:
            action = QAction(self)
            action.setText(text)
            action.triggered.connect(partial(self.compareReferenceWithBibleVersion, text))
            subMenu.addAction(action)
        
        separator = QAction(self)
        separator.setSeparator(True)
        subMenu.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["all"])
        action.triggered.connect(self.compareAllVersions)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["compareReferences"])
        action.setMenu(subMenu)
        self.addAction(action)

        subMenu = QMenu()

        for text in self.parent.parent.textList:
            action = QAction(self)
            action.setText(text)
            action.triggered.connect(partial(self.parallelReferenceWithBibleVersion, text))
            subMenu.addAction(action)
        
        separator = QAction(self)
        separator.setSeparator(True)
        subMenu.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["all"])
        action.triggered.connect(self.compareAllVersions)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["parallelReferences"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        subMenu = QMenu()

        searchBibleReferences = QAction(self)
        searchBibleReferences.setText(config.thisTranslation["openOnNewWindow"])
        searchBibleReferences.triggered.connect(self.displayVersesInNewWindow)
        subMenu.addAction(searchBibleReferences)

        searchBibleReferences = QAction(self)
        searchBibleReferences.setText(config.thisTranslation["bar1_menu"])
        searchBibleReferences.triggered.connect(self.displayVersesInBibleWindow)
        subMenu.addAction(searchBibleReferences)

        searchBibleReferences = QAction(self)
        searchBibleReferences.setText(config.thisTranslation["bottomWindow"])
        searchBibleReferences.triggered.connect(self.displayVersesInBottomWindow)
        subMenu.addAction(searchBibleReferences)

        action = QAction(self)
        action.setText(config.thisTranslation["displayVerses"])
        action.setMenu(subMenu)
        self.addAction(action)

        if self.name in ("main", "study"):

            subMenu = QMenu()
    
            if hasattr(config, "cli"):
                action = QAction(self)
                action.setText(config.thisTranslation["cli"])
                action.triggered.connect(self.switchToCli)
                subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["openOnNewWindow"])
            action.triggered.connect(self.openOnNewWindow)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["menu1_fullScreen"])
            action.triggered.connect(self.openOnFullScreen)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["pdfDocument"])
            action.triggered.connect(self.exportToPdf)
            subMenu.addAction(action)
    
            action = QAction(self)
            action.setText(config.thisTranslation["displayContent"])
            action.setMenu(subMenu)
            self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        if self.name == "main":
            subMenu = QMenu()

            # Instant highlight feature
            action = QAction(self)
            action.setText(config.thisTranslation["menu_highlight"])
            action.triggered.connect(self.instantHighlight)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["remove"])
            action.triggered.connect(self.removeInstantHighlight)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["instantHighlight"])
            action.setMenu(subMenu)
            self.addAction(action)

            separator = QAction(self)
            separator.setSeparator(True)
            self.addAction(separator)

        subMenu = QMenu()

        bibleVerseParser = BibleVerseParser(config.parserStandarisation)
        for bookNo in range(1, 67):
            action = QAction(self)
            action.setText(bibleVerseParser.standardFullBookName[str(bookNo)])
            action.triggered.connect(partial(self.searchSelectedTextInBook, bookNo))
            subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["bibleBook"])
        action.setMenu(subMenu)
        self.addAction(action)

        subMenu = QMenu()

        for text in self.parent.parent.textList:
            action = QAction(self)
            action.setText(text)
            action.triggered.connect(partial(self.searchSelectedText, text))
            subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["bibleVersion"])
        action.setMenu(subMenu)
        self.addAction(action)

        # Search Strong's number bibles, if installed
        if self.parent.parent.strongBibles:
            subMenu = QMenu()
            for text in self.parent.parent.strongBibles:
                action = QAction(self)
                action.setText(text)
                action.triggered.connect(partial(self.searchStrongBible, text))
                subMenu.addAction(action)

            separator = QAction(self)
            separator.setSeparator(True)
            subMenu.addAction(separator)
    
            action = QAction(self)
            action.setText(config.thisTranslation["all"])
            action.triggered.connect(self.searchAllStrongBible)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["bibleConcordance"])
            action.setMenu(subMenu)
            self.addAction(action)

        subMenu = QMenu()
        for keyword in ("SEARCHBOOKNOTE", "SEARCHCHAPTERNOTE", "SEARCHVERSENOTE"):
            action = QAction(self)
            action.setText(config.thisTranslation[keyword])
            action.triggered.connect(partial(self.searchBibleNote, keyword))
            subMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subMenu.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["removeNoteHighlight"])
        action.triggered.connect(self.removeNoteHighlight)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["menu6_notes"])
        action.setMenu(subMenu)
        self.addAction(action)

        subMenu = QMenu()

        searchBibleCharacter = QAction(self)
        searchBibleCharacter.setText(config.thisTranslation["menu5_characters"])
        searchBibleCharacter.triggered.connect(self.searchCharacter)
        subMenu.addAction(searchBibleCharacter)

        searchBibleName = QAction(self)
        searchBibleName.setText(config.thisTranslation["menu5_names"])
        searchBibleName.triggered.connect(self.searchName)
        subMenu.addAction(searchBibleName)

        searchBibleLocation = QAction(self)
        searchBibleLocation.setText(config.thisTranslation["menu5_locations"])
        searchBibleLocation.triggered.connect(self.searchLocation)
        subMenu.addAction(searchBibleLocation)

        subSubMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchTopic)
        subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.topicListAbb:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchResource, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["menu5_topics"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        subSubMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchDictionary)
        subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.dictionaryListAbb:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchResource, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_dict"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        subSubMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchEncyclopedia)
        subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.encyclopediaListAbb:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchResource, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_encyclopedia"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        subSubMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchHebrewGreekLexicon)
        subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["all"])
        action.triggered.connect(partial(self.searchHebrewGreekLexiconSelected, config.thisTranslation["all"]))
        subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.lexiconList:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchHebrewGreekLexiconSelected, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["menu5_lexicon"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        subSubMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchThirdPartyDictionary)
        subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.thirdPartyDictionaryList:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchThirdPartyDictionarySelected, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["menu5_3rdDict"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["bibleResources"])
        action.setMenu(subMenu)
        self.addAction(action)

        subMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchPreviousBook)
        subMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subMenu.addAction(separator)

        subSubMenu = QMenu()

        for module in config.favouriteBooks:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchSelectedBook, module))
            subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["all"])
        action.triggered.connect(self.searchFavouriteBooks)
        subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_favouriteBooks"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_allBooks"])
        action.triggered.connect(self.searchAllBooks)
        subMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subMenu.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["removeBookHighlight"])
        action.triggered.connect(self.removeBookHighlight)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["installBooks"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        # TEXT-TO-SPEECH feature
        languages = self.parent.parent.getTtsLanguages()
        tts = QAction(self)
        tts.setText("{0} [{1}]".format(config.thisTranslation["context1_speak"], languages[config.ttsDefaultLangauge][1].capitalize()))
        tts.triggered.connect(self.textToSpeech)
        self.addAction(tts)

        if config.isTtsInstalled:
            ttsMenu = QMenu()
            languageCodes = list(languages.keys())
            items = [languages[code][1] for code in languageCodes]
            for index, item in enumerate(items):
                languageCode = languageCodes[index]
                action = QAction(self)
                action.setText(item.capitalize())
                action.triggered.connect(partial(self.textToSpeechLanguage, languageCode))
                ttsMenu.addAction(action)

            tts = QAction(self)
            tts.setText(config.thisTranslation["context1_speak"])
            tts.setMenu(ttsMenu)
            self.addAction(tts)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        # IBM-Watson Translation Service

        # Translate into User-defined Language
        userLanguage = config.userLanguage
        translateText = QAction(self)
        translateText.setText("{0} [{1}]".format(config.thisTranslation["context1_translate"], userLanguage))
        translateText.triggered.connect(self.checkUserLanguage)
        self.addAction(translateText)

        translateMenu = QMenu()
        for index, item in enumerate(Translator.toLanguageNames):
            languageCode = Translator.toLanguageCodes[index]
            action = QAction(self)
            action.setText(item)
            action.triggered.connect(partial(self.selectedTextToSelectedLanguage, languageCode))
            translateMenu.addAction(action)

        watsonTranslate = QAction(self)
        watsonTranslate.setText(config.thisTranslation["watsonTranslator"])
        watsonTranslate.setMenu(translateMenu)

        translateMenu = QMenu()
        for language, languageCode in Languages.googleTranslateCodes.items():
            action = QAction(self)
            action.setText(language)
            action.triggered.connect(partial(self.googleTranslate, languageCode))
            translateMenu.addAction(action)

        googleTranslate = QAction(self)
        googleTranslate.setText(config.thisTranslation["googleTranslate"])
        googleTranslate.setMenu(translateMenu)

        translateWrapper = QAction(self)
        translateWrapper.setText(config.thisTranslation["translate"])
        translateWrapperMenu = QMenu()
        translateWrapperMenu.addAction(watsonTranslate)
        translateWrapperMenu.addAction(googleTranslate)
        translateWrapper.setMenu(translateWrapperMenu)
        self.addAction(translateWrapper)

        # Context menu plugins
        if config.enablePlugins:

            separator = QAction(self)
            separator.setSeparator(True)
            self.addAction(separator)

            subMenu = QMenu()

            for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "context"), "py"):
                if not plugin in config.excludeContextPlugins:
                    action = QAction(self)
                    if "_" in plugin:
                        feature, shortcut = plugin.split("_", 1)
                        action.setText(feature)
                        # The following line does not work
                        #action.setShortcut(QKeySequence(shortcut))
                        self.parent.parent.addContextPluginShortcut(plugin, shortcut)
                    else:
                        action.setText(plugin)
                    action.triggered.connect(partial(self.runPlugin, plugin))
                    subMenu.addAction(action)
            
            separator = QAction(self)
            separator.setSeparator(True)
            subMenu.addAction(separator)

            action = QAction(self)
            action.setText(config.thisTranslation["enableIndividualPlugins"])
            action.triggered.connect(self.parent.parent.enableIndividualPluginsWindow)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["menu_plugins"])
            action.setMenu(subMenu)
            self.addAction(action)

    def runPlugin(self, fileName, selectedText=None):
        if selectedText is None:
            selectedText = self.selectedText().strip()
        config.contextSource = self
        config.pluginContext = selectedText
        script = os.path.join(os.getcwd(), "plugins", "context", "{0}.py".format(fileName))
        self.parent.parent.execPythonFile(script)
        config.pluginContext = ""
        config.contextSource = None

    def messageNoSelection(self):
        self.displayMessage("{0}\n{1}".format(config.thisTranslation["message_run"], config.thisTranslation["selectTextFirst"]))

    def messageNoTtsEngine(self):
        self.displayMessage(config.thisTranslation["message_noSupport"])

    def messageNoTtsVoice(self):
        self.displayMessage(config.thisTranslation["message_noTtsVoice"])

    def copySelectedText(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            self.page().triggerAction(self.page().Copy)

    def copySelectedTextWithReference(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            selectedText = self.selectedText().strip()
            verse = config.mainV
            lastVerse = None
            try:
                firstVerse = re.findall(r'\d+', selectedText)[0]
                lastVerse = re.findall(r'\d+', selectedText)[-1]
                if firstVerse:
                    verse = firstVerse
                    if int(firstVerse) == int(lastVerse):
                        lastVerse = None
            except:
                pass
            reference = self.parent.parent.bcvToVerseReference(config.mainB, config.mainC, verse)
            if lastVerse:
                reference += "-" + lastVerse
            text = "{0} ({1})\n{2}".format(reference, config.mainText, selectedText)
            QApplication.clipboard().setText(text)

    def copyHtmlCode(self):
        #self.page().runJavaScript("document.documentElement.outerHTML", 0, self.copyHtmlToClipboard)
        self.page().toHtml(self.copyHtmlToClipboard)

    def copyHtmlToClipboard(self, html):
        QApplication.clipboard().setText(html)

    # Instant highligh feature
    def instantHighlight(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            config.instantHighlightString = selectedText
            self.parent.parent.reloadCurrentRecord()

    def removeInstantHighlight(self):
        if config.instantHighlightString:
            config.instantHighlightString = ""
            self.parent.parent.reloadCurrentRecord()

    # Translate selected words into Selected Language (Google Translate)
    # Url format to translate a phrase:
    # http://translate.google.com/#origin_language_or_auto|destination_language|encoded_phrase
    # or
    # http://translate.google.com/translate?js=n&sl=auto&tl=destination_language&text=encoded_phrase
    # Url format to translate a webpage:
    # http://translate.google.com/translate?js=n&sl=auto&tl=destination_language&u=http://example.net
    def googleTranslate(self, language):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            selectedText = TextUtil.plainTextToUrl(selectedText)
            url = "https://translate.google.com/?sl=origin_language_or_auto&tl={0}&text={1}&op=translate".format(language, selectedText)
            webbrowser.open(url)

    # Translate selected words into Selected Language (Watson Translator)
    def selectedTextToSelectedLanguage(self, language):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            self.translateTextIntoUserLanguage(selectedText, language)

    # Check if config.userLanguage is set
    def checkUserLanguage(self):
        # Use IBM Watson service to translate text
        translator = Translator()
        if translator.language_translator is not None:
            if config.userLanguage and config.userLanguage in Translator.toLanguageNames:
                selectedText = self.selectedText().strip()
                if not selectedText:
                    self.messageNoSelection()
                else:
                    userLanguage = Translator.toLanguageCodes[Translator.toLanguageNames.index(config.userLanguage)]
                    self.translateTextIntoUserLanguage(selectedText, userLanguage)
            else:
                self.parent.parent.openTranslationLanguageDialog()
        else:
            self.parent.parent.displayMessage(config.thisTranslation["ibmWatsonNotEnalbed"])
            config.mainWindow.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/IBM-Watson-Language-Translator")

    # Translate selected words into user-defined language
    def translateTextIntoUserLanguage(self, text, userLanguage="en"):
        # Use IBM Watson service to translate text
        translator = Translator()
        if translator.language_translator is not None:
            translation = translator.translate(text, None, userLanguage)
            self.openPopover(html=translation)
        else:
            self.parent.parent.displayMessage(config.thisTranslation["ibmWatsonNotEnalbed"])
            config.mainWindow.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/IBM-Watson-Language-Translator")

    # TEXT-TO-SPEECH feature
    def textToSpeech(self):
        if config.isTtsInstalled:
            selectedText = self.selectedText().strip()
            if not selectedText:
                self.messageNoSelection()
            elif config.isLangdetectInstalled and config.useLangDetectOnTts:
                from langdetect import detect, DetectorFactory
                DetectorFactory.seed = 0
                # https://pypi.org/project/langdetect/
                language = detect(selectedText)
                speakCommand = "SPEAK:::{0}:::{1}".format(language, selectedText)
                self.parent.parent.textCommandChanged(speakCommand, self.name)
            else:
                speakCommand = "SPEAK:::{0}".format(selectedText)
                self.parent.parent.textCommandChanged(speakCommand, self.name)
        else:
            self.messageNoTtsEngine()

    def textToSpeechLanguage(self, language):
        if config.isTtsInstalled:
            selectedText = self.selectedText().strip()
            if not selectedText:
                self.messageNoSelection()
            speakCommand = "SPEAK:::{0}:::{1}".format(language, selectedText)
            self.parent.parent.textCommandChanged(speakCommand, self.name)
        else:
            self.messageNoTtsEngine()

    def searchPanel(self, selectedText=None):
        if selectedText is None:
            selectedText = self.selectedText().strip()
        if selectedText:
            config.contextItem = selectedText
        self.parent.parent.openControlPanelTab(3)

    def searchSelectedText(self, text=None):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(self.getText() if text is None or not text else text, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def openReferencesInBook(self, book):
        selectedText = self.selectedText().strip()
        command = "{0} {1}".format(book, selectedText) if selectedText else book
        self.parent.parent.textCommandChanged(command, self.name)

    def searchSelectedTextInBook(self, book=None):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "ADVANCEDSEARCH:::{0}:::Book = {1} AND Scripture LIKE '%{2}%'".format(self.getText(), self.getBook() if book is None or not book else book, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedFavouriteBible(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(config.favouriteBible, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedTextOriginal(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format("MOB", selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchHebrewGreekLexicon(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "LEXICON:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchHebrewGreekLexiconSelected(self, module):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHLEXICON:::{0}:::{1}".format(module, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchPreviousBook(self):
        self.searchSelectedBook(config.book)

    def searchSelectedBook(self, book):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHBOOK:::{0}:::{1}".format(book, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchFavouriteBooks(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHBOOK:::FAV:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchAllBooks(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHBOOK:::ALL:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def removeBookHighlight(self):
        if config.bookSearchString:
            config.bookSearchString = ""
            self.parent.parent.reloadCurrentRecord()

    def searchBibleNote(self, keyword):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "{0}:::{1}".format(keyword, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def removeNoteHighlight(self):
        if config.noteSearchString:
            config.noteSearchString = ""
            self.parent.parent.reloadCurrentRecord()

    def searchStrongBible(self, module):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        elif re.match("^[EGH][0-9]+?$", selectedText):
            searchCommand = "CONCORDANCE:::{0}:::{1}".format(module, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)
        else:
            self.parent.parent.displayMessage(config.thisTranslation["notStrongNumber"])

    def searchAllStrongBible(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        elif re.match("^[EGH][0-9]+?$", selectedText):
            searchCommand = "STRONGBIBLE:::ALL:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)
        else:
            self.parent.parent.displayMessage(config.thisTranslation["notStrongNumber"])

    def searchResource(self, module):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTOOL:::{0}:::{1}".format(module, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchCharacter(self):
        self.searchResource("EXLBP")

    def searchName(self):
        self.searchResource("HBN")

    def searchLocation(self):
        self.searchResource("EXLBL")

    def searchTopic(self):
        self.searchResource(config.topic)

    def searchDictionary(self):
        self.searchResource(config.dictionary)

    def searchEncyclopedia(self):
        self.searchResource(config.encyclopedia)

    def searchThirdPartyDictionary(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(config.thirdDictionary, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchThirdPartyDictionarySelected(self, module):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(module, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def exportToPdf(self):
        if self.name == "main":
            self.parent.parent.printMainPage()
        elif self.name == "study":
            self.parent.parent.printStudyPage()

    def openOnNewWindow(self):
        toolTip = self.parent.mainView.tabToolTip(self.parent.mainView.currentIndex()) if self.name == "main" else self.parent.studyView.tabToolTip(self.parent.studyView.currentIndex())
        if toolTip.lower().endswith(".pdf"):
            openPdfViewerInNewWindow = config.openPdfViewerInNewWindow
            config.openPdfViewerInNewWindow = True
            self.parent.parent.openPdfReader(toolTip, fullPath=True)
            config.openPdfViewerInNewWindow = openPdfViewerInNewWindow
        elif toolTip == "EPUB":
            self.parent.parent.runPlugin("ePub Viewer New Window")
        else:
            #self.page().runJavaScript("document.documentElement.outerHTML", 0, self.openNewWindow)
            self.page().toHtml(self.openNewWindow)

    def openOnFullScreen(self):
        #toolText = self.parent.mainView.tabText(self.parent.mainView.currentIndex()) if self.name == "main" else self.parent.studyView.tabText(self.parent.studyView.currentIndex())
        toolTip = self.parent.mainView.tabToolTip(self.parent.mainView.currentIndex()) if self.name == "main" else self.parent.studyView.tabToolTip(self.parent.studyView.currentIndex())
        if toolTip.lower().endswith(".pdf"):
            openPdfViewerInNewWindow = config.openPdfViewerInNewWindow
            config.openPdfViewerInNewWindow = True
            self.parent.parent.openPdfReader(toolTip, fullPath=True, fullScreen=True)
            config.openPdfViewerInNewWindow = openPdfViewerInNewWindow
        elif toolTip == "EPUB":
            self.parent.parent.runPlugin("ePub Viewer Full Screen")
        else:
            self.page().toHtml(lambda html: self.openNewWindow(html, True))

    def openNewWindow(self, html, fullScreen=False):
        self.openPopover(html=html, fullScreen=fullScreen)

    def displayVersesInBottomWindow(self, selectedText=None):
        if selectedText is None:
            selectedText = self.selectedText().strip()
        if selectedText:
            verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
            if verses:
                html = BiblesSqlite().readMultipleVerses(self.getText(), verses)
                self.parent.parent.displayPlainTextOnBottomWindow(html)
            else:
                self.displayMessage(config.thisTranslation["message_noReference"])
        else:
            self.messageNoSelection()

    def openReferenceInBibleVersion(self, bible):
        selectedText = self.selectedText().strip()
        useLiteVerseParsing = config.useLiteVerseParsing
        config.useLiteVerseParsing = False
        verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
        config.useLiteVerseParsing = useLiteVerseParsing
        if verses:
            command = "BIBLE:::{0}:::{1}".format(bible, selectedText)
        elif not config.openBibleInMainViewOnly and self.name == "study":
            command = "STUDY:::{0}:::{1} {2}:{3}".format(bible, BibleBooks.eng[str(config.studyB)][0], config.studyC, config.studyV)
        else:
            command = "TEXT:::{0}".format(bible)
        self.parent.parent.textCommandChanged(command, self.name)

    def compareReferenceWithBibleVersion(self, bible):
        selectedText = self.selectedText().strip()
        useLiteVerseParsing = config.useLiteVerseParsing
        config.useLiteVerseParsing = False
        verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
        config.useLiteVerseParsing = useLiteVerseParsing
        if verses:
            command = "COMPARE:::{0}_{1}:::{2}".format(config.mainText, bible, selectedText)
        elif not config.openBibleInMainViewOnly and self.name == "study":
            command = "STUDY:::{0}:::{1} {2}:{3}".format(bible, BibleBooks.eng[str(config.studyB)][0], config.studyC, config.studyV)
        else:
            command = "TEXT:::{0}".format(bible)
        self.parent.parent.textCommandChanged(command, self.name)

    def parallelReferenceWithBibleVersion(self, bible):
        selectedText = self.selectedText().strip()
        useLiteVerseParsing = config.useLiteVerseParsing
        config.useLiteVerseParsing = False
        verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
        config.useLiteVerseParsing = useLiteVerseParsing
        if verses:
            command = "PARALLEL:::{0}_{1}:::{2}".format(config.mainText, bible, selectedText)
        elif not config.openBibleInMainViewOnly and self.name == "study":
            command = "STUDY:::{0}:::{1} {2}:{3}".format(bible, BibleBooks.eng[str(config.studyB)][0], config.studyC, config.studyV)
        else:
            command = "TEXT:::{0}".format(bible)
        self.parent.parent.textCommandChanged(command, self.name)

    def compareAllVersions(self):
        selectedText = self.selectedText().strip()
        if selectedText:
            verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
            if verses:
                command = "COMPARE:::{0}".format(selectedText)
                self.parent.parent.textCommandChanged(command, self.name)
            else:
                self.displayMessage(config.thisTranslation["message_noReference"])
        else:
            self.messageNoSelection()

    def displayVersesInNewWindow(self, selectedText=None):
        if selectedText is None:
            selectedText = self.selectedText().strip()
        if selectedText:
            verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
            if verses:
                html = BiblesSqlite().readMultipleVerses(self.getText(), verses)
                self.openPopover(html=html)
            else:
                self.displayMessage(config.thisTranslation["message_noReference"])
        else:
            self.messageNoSelection()

    def displayVersesInBibleWindow(self, selectedText=None):
        if selectedText is None:
            selectedText = self.selectedText().strip()
        if selectedText:
            parser = BibleVerseParser(config.parserStandarisation)
            verses = parser.extractAllReferences(selectedText, False)
            if verses:
                references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verses])
                self.parent.parent.textCommandChanged(references, "main")
            else:
                self.displayMessage(config.thisTranslation["message_noReference"])
            del parser
        else:
            self.messageNoSelection()

    def copyAllReferences(self):
        selectedText = self.selectedText().strip()
        if selectedText:
            parser = BibleVerseParser(config.parserStandarisation)
            verseList = parser.extractAllReferences(selectedText, False)
            if not verseList:
                self.displayMessage(config.thisTranslation["message_noReference"])
            else:
                references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])
                QApplication.clipboard().setText(references)
            del parser
        else:
            self.messageNoSelection()

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserWindow or windowType == QWebEnginePage.WebBrowserTab:
            self.openPopover()
        return super().createWindow(windowType)

    def openPopover(self, name="popover", html="UniqueBible.app", fullScreen=False, screenNo=-1):
        # image options
        if config.exportEmbeddedImages:
            html = self.parent.parent.exportAllImages(html)
        if config.clickToOpenImage:
            html = self.parent.parent.addOpenImageAction(html)
        # format html content
        html = self.parent.parent.wrapHtml(html)
        if not hasattr(self, "popoverView") or not self.popoverView.isVisible:
            self.popoverView = WebEngineViewPopover(self, name, self.name)
        self.popoverView.setHtml(html, config.baseUrl)
        if fullScreen:
            monitor = QDesktopWidget().screenGeometry(screenNo)
            self.popoverView.move(monitor.left(), monitor.top())
            if platform.system() == "Linux":
                # Using self.popoverView.showFullScreen() directly does not work on Linux
                self.popoverView.showMaximized()
                self.popoverView.escKeyPressed()
            else:
                self.popoverView.showFullScreen()
        else:
            self.popoverView.setMinimumWidth(config.popoverWindowWidth)
            self.popoverView.setMinimumHeight(config.popoverWindowHeight)
        self.popoverView.show()
        self.parent.parent.bringToForeground(self.popoverView)

    def openPopoverUrl(self, url, name="popover", fullScreen=False, screenNo=-1):
        if not hasattr(self, "popoverUrlView") or not self.popoverUrlView.isVisible:
            self.popoverUrlView = WebEngineViewPopover(self, name, self.name)
        self.popoverUrlView.load(url)
        if fullScreen:
            monitor = QDesktopWidget().screenGeometry(screenNo)
            self.popoverUrlView.move(monitor.left(), monitor.top())
            if platform.system() == "Linux":
                # Using self.popoverUrlView.showFullScreen() directly does not work on Linux
                self.popoverUrlView.showMaximized()
                self.popoverUrlView.escKeyPressed()
            else:
                self.popoverUrlView.showFullScreen()
        else:
            self.popoverUrlView.setMinimumWidth(config.popoverWindowWidth)
            self.popoverUrlView.setMinimumHeight(config.popoverWindowHeight)
        self.popoverUrlView.show()
        self.parent.parent.bringToForeground(self.popoverUrlView)

    def closePopover(self):
        if hasattr(self, "popoverView"):
            self.popoverView.close()

    def saveHtml(self):
        self.page().toHtml(self.saveHtmlToFile)

    def saveHtmlToFile(self, html):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                "",
                "HTML Files (*.html)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".html"
            file = open(fileName, "w")
            file.write(html)
            file.close()
            self.displayMessage(config.thisTranslation["saved"])


class WebEnginePage(QWebEnginePage):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            # The following line opens a desktop browser
            #QDesktopServices.openUrl(url);

            # url here is a QUrl
            # can redirect to another link, e.g.
            # url = QUrl("https://marvel.bible")
            self.setUrl(url)
            return False
        return True

