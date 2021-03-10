from qtpy.QtCore import QSize
from gui.MenuItems import *
import shortcut as sc
from BiblesSqlite import BiblesSqlite
from util.LanguageUtil import LanguageUtil


class Starter:

    def create_menu(self):

        config.instantMode = 0

        menuBar = self.menuBar()
        # 1st column
        menu = addMenu(menuBar, "menu1_app")
        subMenu0 = addSubMenu(menu, "menu1_preferences")
        subMenu = addSubMenu(subMenu0, "menu1_selectTheme")
        items = (
            ("menu_light_theme", self.setDefaultTheme),
            ("menu1_dark_theme", self.setDarkTheme),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(subMenu0, "menu1_selectMenuLayout")
        items = (
            ("menu1_aleph_menu_layout", lambda: self.setMenuLayout("aleph")),
            ("menu1_focus_menu_layout", lambda: self.setMenuLayout("focus")),
            ("menu1_classic_menu_layout", lambda: self.setMenuLayout("classic")),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu0 = addSubMenu(menu, "languageSettings")
        subMenu = addSubMenu(subMenu0, "menu1_programInterface")
        for language in LanguageUtil.getNamesSupportedLanguages():
            addMenuItem(subMenu, language, self, lambda language=language: self.changeInterfaceLanguage(language), translation=False)
        addMenuItem(menu, "menu_config_flags", self, self.moreConfigOptionsDialog)
        addMenuItem(menu, "menu1_update", self, self.showUpdateAppWindow)
        addIconMenuItem("UniqueBibleApp.png", menu, "menu1_exit", self, self.quitApp, sc.quitApp)

        # 2nd column
        menu = addMenu(menuBar, "menu_bible")
        subMenu = addSubMenu(menu, "menu_navigation")
        items = (
            ("menu_next_book", self.nextMainBook, sc.nextMainBook),
            ("menu_previous_book", self.previousMainBook, sc.previousMainBook),
            ("menu4_next", self.nextMainChapter, sc.nextMainChapter),
            ("menu4_previous", self.previousMainChapter, sc.previousMainChapter),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        menu.addSeparator()
        subMenu = addSubMenu(menu, "add")
        items = (
            ("menu8_bibles", self.installMarvelBibles),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)

        # information
        if config.showInformation:
            menu = addMenu(menuBar, "menu9_information")
            addMenuItem(menu, "latestChanges", self, self.showInfo)
            subMenu = addSubMenu(menu, "menu_support")
            items = (
                ("menu1_wikiPages", self.openUbaWiki, sc.ubaWiki),
                ("menu_discussions", self.openUbaDiscussions, sc.ubaDiscussions),
                ("report", self.reportAnIssue, None),
            )
            for feature, action, shortcut in items:
                addMenuItem(subMenu, feature, self, action, shortcut)
            subMenu = addSubMenu(menu, "websites")
            items = (
                ("BibleTools.app", self.openBibleTools),
                ("UniqueBible.app", self.openUniqueBible),
                ("Marvel.bible", self.openMarvelBible),
                ("BibleBento.com", self.openBibleBento),
                ("OpenGNT.com", self.openOpenGNT),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action, None, False)
            items = (
                ("menu9_contact", self.contactEliranWong),
            )
            for feature, action in items:
                addMenuItem(menu, feature, self, action)
            addMenuItem(menu, "menu9_donate", self, self.donateToUs)

    def setupToolBarStandardIconSize(self):
        
        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        button = QPushButton("<")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_previous_chapter", self.previousMainChapter, self.firstToolBar, button)
        self.mainRefButton = QPushButton(self.verseReference("main")[-1])
        self.addStandardTextButton("bar1_reference", self.mainRefButtonClicked, self.firstToolBar, self.mainRefButton)
        button = QPushButton(">")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_next_chapter", self.nextMainChapter, self.firstToolBar, button)

        # Version selection
        if self.textCommandParser.isDatabaseInstalled("bible"):
            self.versionCombo = QComboBox()
            self.bibleVersions = BiblesSqlite().getBibleList()
            self.versionCombo.addItems(self.bibleVersions)
            initialIndex = 0
            if config.mainText in self.bibleVersions:
                initialIndex = self.bibleVersions.index(config.mainText)
            self.versionCombo.setCurrentIndex(initialIndex)
            self.versionCombo.currentIndexChanged.connect(self.changeBibleVersion)
            self.firstToolBar.addWidget(self.versionCombo)

        self.addStandardIconButton("bar1_searchBible", "search.png", self.displaySearchBibleCommand, self.firstToolBar)
        self.addStandardIconButton("bar1_searchBibles", "search_plus.png", self.displaySearchBibleMenu, self.firstToolBar)

        self.firstToolBar.addSeparator()

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.setClearButtonEnabled(True)
        self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        self.textCommandLineEdit.setMinimumWidth(100)
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        if not config.preferControlPanelForCommandLineEntry:
            self.firstToolBar.addWidget(self.textCommandLineEdit)
            self.firstToolBar.addSeparator()

        # self.enableStudyBibleButton = QPushButton()
        # self.addStandardIconButton(self.getStudyBibleDisplayToolTip(), self.getStudyBibleDisplay(), self.enableStudyBibleButtonClicked, self.firstToolBar, self.enableStudyBibleButton, False)

        # Toolbar height here is affected by the actual size of icon file used in a QAction
        if config.qtMaterial and config.qtMaterialTheme:
            self.firstToolBar.setFixedHeight(config.iconButtonWidth + 4)
            self.firstToolBar.setIconSize(QSize(config.iconButtonWidth / 2, config.iconButtonWidth / 2))
        # QAction can use setVisible whereas QPushButton cannot when it is placed on a toolbar.
        self.studyRefButton = self.firstToolBar.addAction(":::".join(self.verseReference("study")), self.studyRefButtonClicked)
        # iconFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        # self.enableSyncStudyWindowBibleButton = self.firstToolBar.addAction(QIcon(iconFile), self.getSyncStudyWindowBibleDisplayToolTip(), self.enableSyncStudyWindowBibleButtonClicked)
        # if config.openBibleInMainViewOnly:
        #     self.studyRefButton.setVisible(False)
        #     self.enableSyncStudyWindowBibleButton.setVisible(False)
        # self.firstToolBar.addSeparator()

        # self.addStandardIconButton("bar1_toolbars", "toolbar.png", self.hideShowAdditionalToolBar, self.firstToolBar)

        self.secondToolBar = QToolBar()

        # Left tool bar
        self.leftToolBar = QToolBar()

        # Right tool bar
        self.rightToolBar = QToolBar()

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))


    def setupToolBarFullIconSize(self):

        self.leftToolBar = QToolBar()

        self.rightToolBar = QToolBar()

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
