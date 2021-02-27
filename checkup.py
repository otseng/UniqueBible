import config, subprocess
from platform import system
from util.ConfigUtil import ConfigUtil

def pip3InstallModule(module):
    print("Installing missing module '{0}' ...".format(module))
    # implement pip3 as a subprocess:
    install = subprocess.Popen(['pip3', 'install', module], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    *_, stderr = install.communicate()
    return stderr

def isPySide2Installed():
    try:
        from PySide2.QtWidgets import QApplication, QStyleFactory
        return True
    except:
        return False

def isGdownInstalled():
    try:
        import gdown
        return True
    except:
        return False

# [ Required ] babel module
# Internationalization and localization library
# http://babel.pocoo.org/
def isBabelInstalled():
    try:
        from babel import Locale
        return True
    except:
        return False

def isPyPDF2Installed():
    try:
        import PyPDF2
        return True
    except:
        return False

def isPythonDocxInstalled():
    try:
        from docx import Document
        return True
    except:
        return False

def isDiffMatchPatchInstalled():
    try:
        from diff_match_patch import diff_match_patch
        return True
    except:
        return False

def isLangdetectInstalled():
    try:
        from langdetect import detect, detect_langs, DetectorFactory
        return True
    except:
        return False

def isPygithubInstalled():
    try:
        from github import Github, InputFileContent
        return True
    except:
        return False

def isQtMaterialInstalled():
    try:
        from qt_material import apply_stylesheet
        return True
    except:
        return False

def isTelnetlib3Installed():
    try:
        import telnetlib3
        return True
    except:
        return False

def isIbmWatsonInstalled():
    try:
        from ibm_watson import LanguageTranslatorV3
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        return True
    except:
        return False

def isRequestsInstalled():
    try:
        import requests
        return True
    except:
        return False

# [Optional] Translates Chinese characters into pinyin.
def isPypinyinInstalled():
    try:
        from pypinyin import pinyin
        return True
    except:
        return False

def isTtsInstalled():
    if system() == "Linux" and config.espeak:
        espeakInstalled, _ = subprocess.Popen("which espeak", shell=True, stdout=subprocess.PIPE).communicate()
        if not espeakInstalled:
            config.espeak = False
            print("'espeak' is not found.  To set up 'espeak', you may read https://github.com/eliranwong/ChromeOSLinux/blob/main/multimedia/espeak.md")
            return False
        else:
            return True
    else:
        try:
            from PySide2.QtTextToSpeech import QTextToSpeech, QVoice
            return True
        except:
            return False

# Set config values for optional features
def setInstallConfig(module, isInstalled):
    if module == "PyPDF2":
        config.isPyPDF2Installed = isInstalled
    elif module == "python-docx":
        config.isPythonDocxInstalled = isInstalled
    elif module == "diff_match_patch":
        config.isDiffMatchPatchInstalled = isInstalled
    elif module == "langdetect":
        config.isLangdetectInstalled = isInstalled
    elif module == "pygithub":
        config.isPygithubInstalled = isInstalled
    elif module == "qt-material":
        config.isQtMaterialInstalled = isInstalled
    elif module == "telnetlib3":
        config.isTelnetlib3Installed = isInstalled
    elif module == "ibm-watson":
        config.isIbmWatsonInstalled = isInstalled
    elif module == "requests":
        config.isRequestsInstalled = isInstalled
    elif module == "pypinyin":
        config.isPypinyinInstalled = isInstalled

# Check if required modules are installed
required = (
    ("PySide2", "Graphical Interface", isPySide2Installed),
    ("gdown", "Download UBA modules from Google drive", isGdownInstalled),
    ("babel", "Internationalization and localization library", isBabelInstalled),
)
for module, feature, isInstalled in required:
    isInstalled = isInstalled()
    if not isInstalled:
        if pip3InstallModule(module):
            print("Required feature '{0}' is not enabled.\nTo enable it, install python package '{1}' first, by running 'pip3 install {1}' with terminal.".format(feature, module))
            exit(1)

# Check if optional modules are installed
optional = (
    ("PyPDF2", "Open PDF file", isPyPDF2Installed),
    ("python-docx", "Open DOCX file", isPythonDocxInstalled),
    ("diff_match_patch", "Highlight Differences", isDiffMatchPatchInstalled),
    ("langdetect", "Detect Language", isLangdetectInstalled),
    ("pygithub", "Gist-synching notes across devices", isPygithubInstalled),
    ("qt-material", "Qt Material Themes", isQtMaterialInstalled),
    ("telnetlib3", "Telnet Client and Server library", isTelnetlib3Installed),
    ("ibm-watson", "IBM-Watson Language Translator", isIbmWatsonInstalled),
    ("requests", "Download missing files", isRequestsInstalled),
    ("pypinyin", "Chinese pinyin", isPypinyinInstalled),
)
for module, feature, isInstalled in optional:
    isInstalled = isInstalled()
    if not isInstalled:
        if pip3InstallModule(module):
            available = False
            print("Optional feature '{0}' is not enabled.\nTo enable it, install python package '{1}' first, by running 'pip3 install {1}' with terminal.".format(feature, module))
        else:
            available = True
            print("Missing module '{0}' is now installed.".format(module))
    else:
        available = True
    setInstallConfig(module, available)

# Check if other optional features are installed
# [Optional] Text-to-Speech feature
config.isTtsInstalled = isTtsInstalled()
if not config.isTtsInstalled:
    print("Text-to-speech feature is not enabled or supported on your device.")

# Import modules for developer
if config.developer:
    # import exlbl
    pass


