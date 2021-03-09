#!venv/bin/python

# UniqueBible.app
# a cross-platform desktop bible application
# For more information on this application, visit https://BibleTools.app or https://UniqueBible.app.

import os, platform, logging, re, sys
import logging.handlers as handlers
import socket

thisFile = os.path.realpath(__file__)
wd = thisFile[:-7]
if os.getcwd() != wd:
    os.chdir(wd)

# Check argument passed to UBA as a parameter
initialCommand = " ".join(sys.argv[1:]).strip()
initialCommandIsPython = True if initialCommand.endswith(".py") and os.path.isfile(initialCommand) else False

# Create custom files
from util.FileUtil import FileUtil
FileUtil.createCustomFiles()

# Make sure config.py exists before importing config and all other scripts which depends on config
import config
# Setup config values
from util.ConfigUtil import ConfigUtil
ConfigUtil.setup()
# Check for dependencies and other essential elements
from checkup import *

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

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Remote CLI
if (len(sys.argv) > 1) and sys.argv[1] == "cli":
    try:
        import telnetlib3
    except:
        print("Please run 'pip install telnetlib3' to use remote CLI")
        exit(0)

    try:
        import telnetlib3
        import asyncio
        from util.RemoteCliHandler import RemoteCliHandler

        port = 8888
        if (len(sys.argv) > 2):
            port = int(sys.argv[2])
        print("Running in remote CLI Mode on port {0}".format(port))
        print("Access by 'telnet {0} {1}'".format(get_ip(), port))
        print("Press Ctrl-C to stop the server")
        loop = asyncio.get_event_loop()
        coro = telnetlib3.create_server(port=port, shell=RemoteCliHandler.shell)
        server = loop.run_until_complete(coro)
        loop.run_until_complete(server.wait_closed())
        exit(0)
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(str(e))
        exit(-1)

# Setup menu shortcut configuration file
from util.ShortcutUtil import ShortcutUtil
ShortcutUtil.setup(config.menuShortcuts)
# Setup GUI windows
from gui.MainWindow import MainWindow
from qtpy.QtWidgets import QApplication, QStyleFactory
from themes import Themes


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
    if platform.system() == "Linux" and not config.linuxStartFullScreen:
        # Launching the app in full screen in some Linux distributions makes the app too sticky to be resized.
        # Below is a workaround, loading the app in 4/5 of the screen size.
        config.mainWindow.resize(config.screenWidth * 4 / 5, config.screenHeight)
    elif platform.system() == "Windows":
        config.mainWindow.showMaximized()
    else:
        # macOS or Linux set to fullscreen
        config.mainWindow.resize(config.screenWidth, config.screenHeight)
    # pre-load control panel
    config.mainWindow.manageControlPanel(config.showControlPanelOnStartup)
    config.mainWindow.show()

    # Check if migration is needed for version >= 0.56
    config.mainWindow.checkMigration()

def executeInitialTextCommand(textCommand, addRecord=False, source="main"):
    try:
        if source == "main" or (source == "study" and re.match("^online:::", textCommand, flags=re.IGNORECASE)):
            config.mainWindow.textCommandLineEdit.setText(textCommand)
        config.mainWindow.runTextCommand(textCommand, addRecord, source)
    except:
        print("Failed to execute '{0}' on startup.".format(textCommand))

def populateTabsOnStartup(source="main"):
    history = config.history[source]
    for i in reversed(range(config.numberOfTab - 1 if initialCommand and not initialCommandIsPython and source == "main" else config.numberOfTab)):
        index = i + 1
        if len(history) >= index:
            command = history[0 - index]
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
    config.mainWindow.textCommandParser.stopTtsAudio()
    # Run shutdown plugins
    if config.enablePlugins:
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "shutdown"), "py"):
            script = os.path.join(os.getcwd(), "plugins", "shutdown", "{0}.py".format(plugin))
            config.mainWindow.execPythonFile(script)
    ConfigUtil.save()

# Set Qt input method variable to use fcitx / ibus if config.fcitx / config.ibus is "True"
if config.fcitx:
    os.environ["QT_IM_MODULE"] = "fcitx"
elif config.ibus:
    os.environ["QT_IM_MODULE"] = "ibus"

# Set Qt input method variable to use Qt virtual keyboards if config.virtualKeyboard is "True"
if config.virtualKeyboard:
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

# Start PySide2 gui
app = QApplication(sys.argv)
# Assign a function to save configurations when the app is closed.
app.aboutToQuit.connect(exitApplication)
# Apply window style
if config.windowStyle and config.windowStyle in QStyleFactory.keys():
    app.setStyle(config.windowStyle)
# Apply theme style
if config.qtMaterial and config.qtMaterialTheme:
    apply_stylesheet(app, theme=config.qtMaterialTheme)
    config.theme = "dark" if config.qtMaterialTheme.startswith("dark_") else "default"
else:
    app.setPalette(Themes.getPalette())

# Assign mainWindow to config.mainWindow, to make it acessible from user customised user script
config.mainWindow = MainWindow()

# Check screen size
availableGeometry = app.desktop().availableGeometry(config.mainWindow)
setupMainWindow(availableGeometry)

# Run initial commands
if config.populateTabsOnStartup:
    openBibleWindowContentOnNextTab, openStudyWindowContentOnNextTab = config.openBibleWindowContentOnNextTab, config.openStudyWindowContentOnNextTab
    config.openBibleWindowContentOnNextTab = True
    config.openStudyWindowContentOnNextTab = True
    # Execute initial command on Bible Window
    populateTabsOnStartup("main")
    # Execute initial command on Study Window
    populateTabsOnStartup("study")
    config.openBibleWindowContentOnNextTab, config.openStudyWindowContentOnNextTab = openBibleWindowContentOnNextTab, openStudyWindowContentOnNextTab
else:
    # Execute initial command on Bible Window
    if not initialCommand or initialCommandIsPython:
        runLastHistoryRecord("main")
    # Execute initial command on Study Window
    runLastHistoryRecord("study")

if initialCommand and initialCommandIsPython:
    config.mainWindow.execPythonFile(initialCommand)
elif initialCommand:
    executeInitialTextCommand(initialCommand, True)

# Run startup plugins
if config.enablePlugins:
    for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "startup"), "py"):
        script = os.path.join(os.getcwd(), "plugins", "startup", "{0}.py".format(plugin))
        config.mainWindow.execPythonFile(script)

# Set indexes of history records
setCurrentRecord()

# Startup macro
config.mainWindow.runMacro(config.startupMacro)

def global_excepthook(type, value, traceback):
    logger.error("Uncaught exception", exc_info=(type, value, traceback))
    print(traceback.format_exc())

sys.excepthook = global_excepthook

sys.exit(app.exec_())
