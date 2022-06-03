#!venv/bin/python

# UniqueBible.app
# a cross-platform desktop bible application
# For more information on this application, visit https://BibleTools.app or https://UniqueBible.app.
import glob
import os, platform, logging, re, sys, subprocess
import logging.handlers as handlers
from util.FileUtil import FileUtil
from util.NetworkUtil import NetworkUtil
from util.WebtopUtil import WebtopUtil

# Change working directory to UniqueBible directory
thisFile = os.path.realpath(__file__)
wd = thisFile[:-7]
if os.getcwd() != wd:
    os.chdir(wd)

# Create custom files
FileUtil.createCustomFiles()

# Make sure config.py exists before importing config and all other scripts which depends on config
import config
# Setup config values
from util.ConfigUtil import ConfigUtil
ConfigUtil.setup()
from gui.Styles import *

# Check argument passed to UBA as a parameter
initialCommand = " ".join(sys.argv[1:]).strip()
docker = False
config.noQt = False
config.cli = False
if initialCommand == "docker":
    docker = True
    initialCommand = "gui"
    #config.isGTTSInstalled = True
    config.fcitx = True
    config.docker = True
    config.updateWithGitPull = True
    # Force to use PySide2 instead of PyQt5 for general users
    if not config.developer and config.qtLibrary != "pyside2":
        config.qtLibrary = "pyside2"
        os.environ["QT_API"] = config.qtLibrary
    # To deal with "ERROR:command_buffer_proxy_impl.cc(141)] ContextResult::kTransientFailure: Failed to send GpuChannelMsg_CreateCommandBuffer."
    # Reference: https://bugreports.qt.io/browse/QTBUG-82423
    os.environ["QTWEBENGINE_DISABLE_GPU_THREAD"] = "1"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-compositing --num-raster-threads=1 --enable-viewport --main-frame-resizes-are-orientation-changes --disable-composited-antialiasing"
    # Setup yay on first run; latest docker images has /opt/yay in place
    if os.path.isdir("/opt/yay") and not WebtopUtil.isPackageInstalled("yay"):
        print("Installing yay ...")
        os.system("sudo chown -R abc:users /opt/yay && cd /opt/yay && makepkg -si --noconfirm --needed && cd -")
    if WebtopUtil.isPackageInstalled("yay") and not WebtopUtil.isPackageInstalled("wps"):
        print("Installing fonts ...")
        os.system("yay -Syu --noconfirm --needed ttf-wps-fonts ttf-ms-fonts wps-office-fonts")
        print("Installing wps-office ...")
        os.system("yay -Syu --noconfirm --needed wps-office-cn")
else:
    config.docker = False
if initialCommand == "cli":
    config.cli = True
elif initialCommand == "gui":
    initialCommand = ""
elif len(sys.argv) > 1 and sys.argv[1] in ("telnet-server", "http-server", "execute-macro"):
    config.noQt = True
initialCommandIsPython = True if initialCommand.endswith(".py") and os.path.isfile(initialCommand) else False

# Check for dependencies and other essential elements
os.environ["PYTHONUNBUFFERED"] = "1"
from util.checkup import *

if initialCommand == "setup-only":
    print("UniqueBibleApp installed!")
    exit()

# Setup logging
logger = logging.getLogger('uba')
if config.enableLogging:
    logger.setLevel(logging.DEBUG)
    logHandler = handlers.TimedRotatingFileHandler('uba.log', when='D', interval=1, backupCount=0)
    logHandler.setLevel(logging.DEBUG)
    logger.addHandler(logHandler)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
else:
    logger.addHandler(logging.NullHandler())

def cleanupTempFiles():
    files = glob.glob(os.path.join("htmlResources", "main-*.html"))
    for file in files:
        os.remove(file)

cleanupTempFiles()

# Remote CLI
if (len(sys.argv) > 1) and sys.argv[1] == "telnet-server":
    config.runMode = "telnet-server"
    try:
        import telnetlib3
    except:
        print("Please run 'pip install telnetlib3' to use remote CLI")
        exit(0)

    try:
        import telnetlib3
        import asyncio
        from util.RemoteCliHandler import RemoteCliHandler

        port = config.telnetServerPort
        if (len(sys.argv) > 2):
            port = int(sys.argv[2])
        print("Running in remote CLI Mode on port {0}".format(port))
        print("Access by 'telnet {0} {1}'".format(NetworkUtil.get_ip(), port))
        print("Press Ctrl-C to stop the server")
        loop = asyncio.get_event_loop()
        coro = telnetlib3.create_server(port=port, shell=RemoteCliHandler.shell)
        server = loop.run_until_complete(coro)
        loop.run_until_complete(server.wait_closed())
        ConfigUtil.save()
        exit(0)
    except KeyboardInterrupt:
        ConfigUtil.save()
        exit(0)
    except Exception as e:
        print(str(e))
        exit(-1)

# Run startup plugins
def runStartupPlugins():
    if config.enablePlugins:
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "startup"), "py"):
            if not plugin in config.excludeStartupPlugins:
                script = os.path.join(os.getcwd(), "plugins", "startup", "{0}.py".format(plugin))
                config.mainWindow.execPythonFile(script)

# HTTP Server
from db.BiblesSqlite import BiblesSqlite

def checkMigration():
    if config.version >= 0.56:
        biblesSqlite = BiblesSqlite()
        biblesWithBothVersions = biblesSqlite.migratePlainFormattedBibles()
        if biblesWithBothVersions:
            biblesSqlite.proceedMigration(biblesWithBothVersions)
        if config.migrateDatabaseBibleNameToDetailsTable:
            biblesSqlite.migrateDatabaseContent()
        del biblesSqlite

def startHttpServer():
    import socketserver
    from util.RemoteHttpHandler import RemoteHttpHandler

    config.restartHttpServer = False
    port = config.httpServerPort
    if (len(sys.argv) > 2):
        port = int(sys.argv[2])
    config.thisHttpServerPort = port
    print("Running in HTTP Server Mode")
    print("Open browser link: 'http://{0}:{1}'".format(NetworkUtil.get_ip(), port))
    socketserver.TCPServer.allow_reuse_address = True
    config.enableHttpServer = True
    with socketserver.TCPServer(("", port), RemoteHttpHandler) as httpd:
        while config.enableHttpServer:
            httpd.handle_request()
        httpd.server_close()
        cleanupTempFiles()
        print("Server is stopped!")

config.enableHttpServer = False
if (len(sys.argv) > 1) and sys.argv[1] == "http-server":
    config.runMode = "http-server"
    checkMigration()
    startHttpServer()
    ConfigUtil.save()
    if config.restartHttpServer:
        subprocess.Popen("{0} {1} http-server".format(sys.executable, config.httpServerUbaFile), shell=True)
    exit(0)

def printContentOnConsole(text):
    if not "html-text" in sys.modules:
        import html_text
    print(html_text.extract_text(text))
    #subprocess.Popen(["echo", html_text.extract_text(text)])
    #sys.stdout.flush()
    return text

# Execute macro
if (len(sys.argv) > 1) and sys.argv[1] == "execute-macro":
    config.runMode = "execute-macro"
    if config.enableMacros:
        from util.MacroParser import MacroParser
        if len(sys.argv) < 3:
            print("Please specify macro file to run")
            exit(-1)
        file = sys.argv[2]
        if os.path.isfile(os.path.join(MacroParser.macros_dir, file)):
            from util.RemoteCliMainWindow import RemoteCliMainWindow
            config.bibleWindowContentTransformers.append(printContentOnConsole)
            config.studyWindowContentTransformers.append(printContentOnConsole)
            MacroParser(RemoteCliMainWindow()).parse(file)
            ConfigUtil.save()
            print("Macro {0} executed".format(file))
        else:
            print("Macro {0} does not exist".format(file))
    else:
        print("Macros are not enabled")
    exit(0)

# Setup menu shortcut configuration file
if not platform.system() == "Windows" and not config.enableHttpServer:
    import readline
from util.ShortcutUtil import ShortcutUtil
ShortcutUtil.setup(config.menuShortcuts)
# Setup GUI windows
from util.LanguageUtil import LanguageUtil
from functools import partial
from gui.MainWindow import MainWindow
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QApplication, QStyleFactory
    from PySide6.QtWidgets import QMenu, QSystemTrayIcon
    from PySide6.QtGui import QAction, QIcon
else:
    from qtpy.QtWidgets import QApplication, QStyleFactory
    from qtpy.QtWidgets import QMenu, QSystemTrayIcon, QAction
    from qtpy.QtGui import QIcon
from util.themes import Themes
# [Optional] qt-material
# qt-material have to be imported after PySide2
if config.qtMaterial and not config.isQtMaterialInstalled:
    config.qtMaterial = False
if config.qtMaterial:
    from qt_material import apply_stylesheet


# Set screen size at first launch
def setupMainWindow(availableGeometry):
    config.screenWidth = availableGeometry.width()
    config.screenHeight = availableGeometry.height()
    # Check os with platform.system() or sys.platform
    # Linux / Darwin / Windows
    if docker or config.startFullScreen or (platform.system() == "Linux" and config.linuxStartFullScreen):
        config.mainWindow.showFullScreen()
    elif platform.system() == "Linux" and not config.linuxStartFullScreen:
        # Launching the app in full screen in some Linux distributions makes the app too sticky to be resized.
        config.mainWindow.resize(int(config.screenWidth), int(config.screenHeight - 60))
        # Below is an alternate workaround, loading the app in 4/5 of the screen size.
        #config.mainWindow.resize(int(config.screenWidth * 4 / 5), int(config.screenHeight))
    elif platform.system() == "Windows" and hasattr(config, "cli") and not config.cli:
        config.mainWindow.showMaximized()
    else:
        # macOS or Linux set to fullscreen
        config.mainWindow.resize(int(config.screenWidth), int(config.screenHeight))
    # pre-load control panel
    config.mainWindow.manageControlPanel(config.showControlPanelOnStartup)
    if hasattr(config, "cli") and config.cli:
        config.mainWindow.hide()
    else:
        config.mainWindow.show()

    # Check if migration is needed for version >= 0.56
    config.mainWindow.checkMigration()

def executeInitialTextCommand(textCommand, addRecord=False, source="main"):
    try:
        if source == "main" or (source == "study" and re.match("^online:::", textCommand, flags=re.IGNORECASE)):
            config.mainWindow.textCommandLineEdit.setText(textCommand)
        config.mainWindow.runTextCommand(textCommand, addRecord, source, True)
    except:
        print("Failed to execute '{0}' on startup.".format(textCommand))

def populateTabsOnStartup(source="main"):
    # numTabs = config.numberOfTab-1 if initialCommand and not initialCommandIsPython and not (hasattr(config, "cli") and config.cli) and source == "main" else config.numberOfTab
    numTabs = config.numberOfTab
    for i in range(numTabs):
        if str(i) in config.tabHistory[source]:
            command = config.tabHistory[source][str(i)]
            if command:
                previous = i - 1
                if previous < 0:
                    previous = config.numberOfTab - 1
                if source == "main":
                    config.mainWindow.mainView.setCurrentIndex(previous)
                elif source == "study":
                    config.mainWindow.studyView.setCurrentIndex(previous)
                executeInitialTextCommand(command, False, source)

def runLastHistoryRecord(source="main"):
    history = config.history[source]
    command = history[-1]
    executeInitialTextCommand(command, False, source)

def setCurrentRecord():
    mainRecordPosition = len(config.history["main"]) - 1
    studyRecordPosition = len(config.history["study"]) - 1
    config.currentRecord = {'main': mainRecordPosition, 'study': studyRecordPosition}

def exitApplication():
    if not config.doNotStop3rdPartyMediaPlayerOnExit:
        config.mainWindow.closeMediaPlayer()
    # Run shutdown plugins
    if config.enablePlugins:
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "shutdown"), "py"):
            if not plugin in config.excludeShutdownPlugins:
                script = os.path.join(os.getcwd(), "plugins", "shutdown", "{0}.py".format(plugin))
                config.mainWindow.execPythonFile(script)
    ConfigUtil.save()
    if config.docker and config.restartUBA:
        os.system("nohup ./UniqueBibleApp.sh > /dev/null 2>&1 &")
    elif config.restartUBA and hasattr(config, "cli"):
        subprocess.Popen("{0} uba.py gui".format(sys.executable), shell=True)

def nameChanged():
    if app.applicationName() == "UniqueBible.app CLI":
        switchToCli()

def getCommandDocumentation():
    print("\nUBA commands:")
    print("\n".join([re.sub("            #", "#", value[-1]) for value in config.mainWindow.textCommandParser.interpreters.values()]))

def startWithCli():
    if not "html-text" in sys.modules:
        import html_text
    # Cli input
    #config.mainWindow.hide()
    #config.cli = True
    #config.printContentOnConsole = printContentOnConsole
    config.bibleWindowContentTransformers.append(printContentOnConsole)
    config.studyWindowContentTransformers.append(printContentOnConsole)
    while config.cli:
        print("--------------------")
        print("Enter '.bible' to read bible text, '.study' to read study resource, '.help' to read UBA command reference, '.gui' to launch gui, '.quit' to quit,")
        command = input("or UBA command: ").strip()
        if command == ".gui":
            del config.bibleWindowContentTransformers[-1]
            del config.studyWindowContentTransformers[-1]
            config.cli = False
        elif command == ".bible":
            print(html_text.extract_text(config.bibleWindowContent))
            # The following line does not work on Windows on UBA startup
            #config.mainWindow.mainPage.runJavaScript("document.documentElement.outerHTML", 0, printContentOnConsole)
        elif command == ".study":
            print(html_text.extract_text(config.studyWindowContent))
            # The following line does not work on Windows on UBA startup
            #config.mainWindow.studyPage.runJavaScript("document.documentElement.outerHTML", 0, printContentOnConsole)
        elif command in (".help", ".command"):
            getCommandDocumentation()
        elif command == ".quit":
            ConfigUtil.save()
            exit()
        else:
            config.mainWindow.runTextCommand(command)
    config.mainWindow.show()
    if platform.system() == "Windows":
        config.mainWindow.showMaximized()

def switchToCli():
    if not "html-text" in sys.modules:
        import html_text
    # Print content where is context menu was called from
    if config.pluginContext == "study":
        print(html_text.extract_text(config.studyWindowContent))
    else:
        print(html_text.extract_text(config.bibleWindowContent))
    # Hide gui
    if platform.system() == "Darwin":
        config.mainWindow.showMinimized()
    else:
        config.mainWindow.hide()
    # Cli input
    config.cli = True
    toQuit = False
    #config.printContentOnConsole = printContentOnConsole
    config.bibleWindowContentTransformers.append(printContentOnConsole)
    config.studyWindowContentTransformers.append(printContentOnConsole)
    while config.cli:
        print("--------------------")
        print("Enter '.bible' to read bible text, '.study' to read study resource, '.help' to read UBA command reference, '.gui' to launch gui, '.quit' to quit,")
        command = input("or UBA command: ").strip()
        if command == ".gui":
            del config.bibleWindowContentTransformers[-1]
            del config.studyWindowContentTransformers[-1]
            config.cli = False
        elif command == ".bible":
            print(html_text.extract_text(config.bibleWindowContent))
        elif command == ".study":
            print(html_text.extract_text(config.studyWindowContent))
        elif command in (".help", ".command"):
            getCommandDocumentation()
        elif command == ".quit":
            toQuit = True
            config.cli = False
        else:
            config.mainWindow.runTextCommand(command)
    if toQuit:
        config.mainWindow.quitApp()
    else:
        app.setApplicationName("UniqueBible.app")
        if platform.system() == "Darwin":
            config.mainWindow.showMaximized()
            config.mainWindow.raise_()
        else:
            config.mainWindow.show()


# Set Qt input method variable to use fcitx / ibus if config.fcitx / config.ibus is "True"
if config.fcitx:
    os.environ["QT_IM_MODULE"] = "fcitx"
elif config.ibus:
    os.environ["QT_IM_MODULE"] = "ibus"

# Set Qt input method variable to use Qt virtual keyboards if config.virtualKeyboard is "True"
if config.virtualKeyboard:
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

# Start PySide2 gui
config.startup = True
config.thisTranslation = LanguageUtil.loadTranslation(config.displayLanguage)
app = QApplication(sys.argv)

# Set application name
app.setApplicationName("UniqueBible.app")
app.setApplicationDisplayName("UniqueBible.app")
# When application name is changed
app.applicationNameChanged.connect(nameChanged)
# Assign a function to save configurations when the app is closed.
app.aboutToQuit.connect(exitApplication)
# Apply window style
if config.windowStyle and config.windowStyle in QStyleFactory.keys():
    app.setStyle(config.windowStyle)
# Apply theme style
config.defineStyle()
if config.menuLayout == "material":
    app.setPalette(Themes.getPalette())
    app.setStyleSheet(config.materialStyle)
elif config.qtMaterial and config.qtMaterialTheme:
    apply_stylesheet(app, theme=config.qtMaterialTheme)
    config.theme = "dark" if config.qtMaterialTheme.startswith("dark_") else "default"
else:
    app.setPalette(Themes.getPalette())

# Active verse number colour
#config.activeVerseNoColour = config.darkThemeActiveVerseColor if config.theme == "dark" else config.lightThemeActiveVerseColor

# Assign mainWindow to config.mainWindow, to make it acessible from user customised user script
config.studyTextTemp = config.studyText
config.mainWindow = MainWindow()

# Check screen size
availableGeometry = config.mainWindow.screen().availableGeometry()
setupMainWindow(availableGeometry)

# A container of functions to be run after UBA loaded history records on startup
# This offers a way for startup plugins to run codes after history records being loaded.
config.actionsRightAfterLoadingHistoryRecords = []

runStartupPlugins()

# Run initial commands
if config.populateTabsOnStartup:
    openBibleWindowContentOnNextTab, openStudyWindowContentOnNextTab = config.openBibleWindowContentOnNextTab, config.openStudyWindowContentOnNextTab
    forceGenerateHtml = config.forceGenerateHtml
    syncStudyWindowBibleWithMainWindow = config.syncStudyWindowBibleWithMainWindow
    config.openBibleWindowContentOnNextTab = True
    config.openStudyWindowContentOnNextTab = True
    config.forceGenerateHtml = False
    config.syncStudyWindowBibleWithMainWindow = False
    # Execute initial command on Study Window
    populateTabsOnStartup("study")
    # Execute initial command on Bible Window
    populateTabsOnStartup("main")
    config.openBibleWindowContentOnNextTab, config.openStudyWindowContentOnNextTab = openBibleWindowContentOnNextTab, openStudyWindowContentOnNextTab
    config.forceGenerateHtml = forceGenerateHtml
    config.syncStudyWindowBibleWithMainWindow = syncStudyWindowBibleWithMainWindow
elif not config.disableLoadLastOpenFilesOnStartup:
    # Execute initial command on Bible Window
    if not initialCommand or initialCommandIsPython or (hasattr(config, "cli") and config.cli):
        runLastHistoryRecord("main")
    # Execute initial command on Study Window
    history = config.history["study"]
    command = history[-1] if len(history) > 0 else ""
    if not (config.disableOpenPopupWindowOnStartup and command.lower().startswith("book:::")):
        runLastHistoryRecord("study")

# Run functions placed with startup plugins
if config.actionsRightAfterLoadingHistoryRecords:
    for action in config.actionsRightAfterLoadingHistoryRecords:
        action()

# Startup macro
config.mainWindow.runMacro(config.startupMacro)

if initialCommand == "cli":
    if config.isHtmlTextInstalled:
        startWithCli()
    else:
        config.cli = False
        print("CLI feature is not enabled!  Install module 'html-text' first, by running 'pip3 install html-text'!")
elif initialCommand and initialCommandIsPython:
    config.mainWindow.execPythonFile(initialCommand)
elif initialCommand:
    executeInitialTextCommand(initialCommand, True)

# Set indexes of history records
setCurrentRecord()

def global_excepthook(type, value, traceback):
    logger.error("Uncaught exception", exc_info=(type, value, traceback))
    print(traceback.format_exc())

sys.excepthook = global_excepthook


# To work with system tray
if config.enableSystemTray:
    # Set up tray icon
    app.setQuitOnLastWindowClosed(False)
    if not os.path.isfile(config.desktopUBAIcon):
        config.desktopUBAIcon = os.path.join("htmlResources", "UniqueBibleApp.png")
    trayIcon = QIcon(config.desktopUBAIcon)
    tray = QSystemTrayIcon()
    tray.setIcon(trayIcon)
    tray.setVisible(True)
    trayMenu = QMenu()
    # Show Main Window
    showMainWindow = QAction(config.thisTranslation["show"])
    showMainWindow.triggered.connect(config.mainWindow.showFromTray)
    trayMenu.addAction(showMainWindow)
    # Add a separator
    trayMenu.addSeparator()
    # Control Panel
    masterControl = QAction(config.thisTranslation["controlPanel"])
    masterControl.triggered.connect(config.mainWindow.showFromTray)
    masterControl.triggered.connect(partial(config.mainWindow.openControlPanelTab, 0))
    trayMenu.addAction(masterControl)
    miniControl = QAction(config.thisTranslation["menu1_miniControl"])
    miniControl.triggered.connect(config.mainWindow.showFromTray)
    miniControl.triggered.connect(config.mainWindow.manageMiniControl)
    trayMenu.addAction(miniControl)
    # Add a separatorJohn 3:16, 19
    trayMenu.addSeparator()
    # Search section
    searchBibleForClipboardContent = QAction(config.thisTranslation["searchBibleForClipboardContent"])
    searchBibleForClipboardContent.triggered.connect(config.mainWindow.showFromTray)
    searchBibleForClipboardContent.triggered.connect(config.mainWindow.searchBibleForClipboardContent)
    trayMenu.addAction(searchBibleForClipboardContent)
    searchResourcesForClipboardContent = QAction(config.thisTranslation["searchOtherResources"])
    searchResourcesForClipboardContent.triggered.connect(config.mainWindow.showFromTray)
    searchResourcesForClipboardContent.triggered.connect(config.mainWindow.searchResourcesForClipboardContent)
    trayMenu.addAction(searchResourcesForClipboardContent)
    # Add a separatorJohn 3:16, 19
    trayMenu.addSeparator()
    # Work with clipboard
    openClipboardReferences = QAction(config.thisTranslation["openClipboardReferences"])
    openClipboardReferences.triggered.connect(config.mainWindow.showFromTray)
    openClipboardReferences.triggered.connect(config.mainWindow.openReferencesOnClipboard)
    trayMenu.addAction(openClipboardReferences)
    displayClipboardContent = QAction(config.thisTranslation["displayClipboardContent"])
    displayClipboardContent.triggered.connect(config.mainWindow.showFromTray)
    displayClipboardContent.triggered.connect(config.mainWindow.pasteFromClipboard)
    trayMenu.addAction(displayClipboardContent)
    if not config.noTtsFound:
        readClipboardContent = QAction(config.thisTranslation["readClipboardContent"])
        readClipboardContent.triggered.connect(config.mainWindow.readClipboardContent)
        trayMenu.addAction(readClipboardContent)
    runClipboardCommand = QAction(config.thisTranslation["runClipboardCommand"])
    runClipboardCommand.triggered.connect(config.mainWindow.showFromTray)
    runClipboardCommand.triggered.connect(config.mainWindow.parseContentOnClipboard)
    trayMenu.addAction(runClipboardCommand)
    # Context plugins
    if config.enablePlugins:
        subMenu = QMenu()
        for index, plugin in enumerate(FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "context"), "py")):
            feature, *_ = plugin.split("_", 1)
            exec("action{0} = QAction(feature)".format(index))
            exec("action{0}.triggered.connect(partial(config.mainWindow.runContextPluginOnClipboardContent, plugin))".format(index))
            exec("subMenu.addAction(action{0})".format(index))
        contextPlugins = QAction(config.thisTranslation["runContextPluginOnClipboardContent"])
        contextPlugins.setMenu(subMenu)
        trayMenu.addAction(contextPlugins)
    # Add a separator
    trayMenu.addSeparator()
    # Media
    youtubeDownloader = QAction(config.thisTranslation["youtube_utility"])
    youtubeDownloader.triggered.connect(config.mainWindow.showFromTray)
    youtubeDownloader.triggered.connect(config.mainWindow.openYouTube)
    trayMenu.addAction(youtubeDownloader)
    showMedia = QAction(config.thisTranslation["media"])
    showMedia.triggered.connect(config.mainWindow.showFromTray)
    showMedia.triggered.connect(partial(config.mainWindow.openControlPanelTab, 6))
    trayMenu.addAction(showMedia)
    stopPlayMedia = QAction(config.thisTranslation["stopPlayMedia"])
    stopPlayMedia.triggered.connect(config.mainWindow.closeMediaPlayer)
    trayMenu.addAction(stopPlayMedia)
    # Add a separator
    trayMenu.addSeparator()
    # Restart UBA on macOS
    if platform.system() == "Darwin":
        restartApp = QAction(config.thisTranslation["restart"])
        restartApp.triggered.connect(config.mainWindow.restartApp)
        trayMenu.addAction(restartApp)
    # Quit
    quitApp = QAction(config.thisTranslation["menu_quit"])
    quitApp.triggered.connect(app.quit)
    trayMenu.addAction(quitApp)
    tray.setContextMenu(trayMenu)

# Launch UBA
config.restartUBA = False
sys.exit(app.exec() if config.qtLibrary == "pyside6" else app.exec_())
