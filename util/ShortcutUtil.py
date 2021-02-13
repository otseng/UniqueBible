import glob
import pprint

from os import path
from PySide2.QtCore import Qt

from util.FileUtil import FileUtil


class ShortcutUtil:

    brachysData = {
        "back": "Ctrl+[",
        "bookFeatures": "Ctrl+L, F",
        "bottomHalfScreenHeight": "Ctrl+S,2",
        "chapterFeatures": "Ctrl+L, H",
        "commentaryRefButtonClicked": "Ctrl+Y",
        "createNewNoteFile": "Ctrl+N",
        "cycleInstant": "Ctrl+T",
        "displaySearchAllBookCommand": "Ctrl+S, R",
        "displaySearchBibleCommand": "Ctrl+1",
        "displaySearchBibleMenu": "Ctrl+S, M",
        "displaySearchBookCommand": "Ctrl+5",
        "displaySearchHighlightCommand": "Ctrl+S, H",
        "displaySearchStudyBibleCommand": "Ctrl+2",
        "editExternalFileButtonClicked": "Ctrl+N, E",
        "enableInstantButtonClicked": "Ctrl+=",
        "enableParagraphButtonClicked": "Ctrl+P",
        "enableSubheadingButtonClicked": "Ctrl+D, P",
        "externalFileButtonClicked": "Ctrl+N, R",
        "forward": "Ctrl+]",
        "fullsizeWindow": "Ctrl+S,F",
        "gotoFirstChapter": None,
        "gotoLastChapter": None,
        "hideShowAdditionalToolBar": "Ctrl+G",
        "hideShowLeftToolBar": "Ctrl+T, L",
        "hideShowMainToolBar": "Ctrl+T, 1",
        "hideShowRightToolBar": "Ctrl+T, R",
        "hideShowSecondaryToolBar": "Ctrl+T,3",
        "largerFont": "Ctrl++",
        "leftHalfScreenWidth": "Ctrl+S,3",
        "mainHistoryButtonClicked": "Ctrl+'",
        "mainPageScrollPageDown": "Ctrl+H,5",
        "mainPageScrollPageUp": "Ctrl+H,4",
        "mainPageScrollToTop": "Ctrl+H,3",
        "manageControlPanel": "Ctrl+M",
        "manageRemoteControl": None,
        "masterCurrentIndex0": 'B',
        "masterCurrentIndex1": 'L',
        "masterCurrentIndex2": 'F',
        "masterCurrentIndex3": 'H',
        "masterHide": 'H',
        "nextChapterButton": "Ctrl+)",
        "nextMainBook": "Ctrl+H,1",
        "nextMainChapter": "Ctrl+>",
        "openControlPanelTab0": 'Ctrl+B',
        "openControlPanelTab1": 'Ctrl+L',
        "openControlPanelTab2": 'Ctrl+F',
        "openControlPanelTab3": 'Ctrl+H',
        "openMainBookNote": "Ctrl+N, B",
        "openMainChapterNote": "Ctrl+N, C",
        "openMainVerseNote": "Ctrl+N, V",
        "openTextFileDialog": "Ctrl+O",
        "parallel": "Ctrl+W",
        "parseContentOnClipboard": "Ctrl+^",
        "previousChapterButton": "Ctrl+(",
        "previousMainBook": "Ctrl+H,2",
        "previousMainChapter": "Ctrl+<",
        "quitApp": "Ctrl+Q",
        "reloadCurrentRecord": "Ctrl+D, R",
        "rightHalfScreenWidth": "Ctrl+S,4",
        "runCOMBO": "Ctrl+K",
        "runCOMMENTARY": "Ctrl+Y",
        "runCOMPARE": "Ctrl+D",
        "runCROSSREFERENCE": "Ctrl+R",
        "runDISCOURSE": "Ctrl+L, D",
        "runINDEX": "Ctrl+.",
        "runKJV2Bible": None,
        "runMAB": "Ctrl+B, 5",
        "runMIB": "Ctrl+B, 2",
        "runMOB": "Ctrl+B, 1",
        "runMPB": "Ctrl+B, 4",
        "runMTB": "Ctrl+B, 3",
        "runTSKE": "Ctrl+E",
        "runTransliteralBible": None,
        "runWORDS": "Ctrl+L, W",
        "searchCommandBibleCharacter": "Ctrl+7",
        "searchCommandBibleDictionary": "Ctrl+3",
        "searchCommandBibleEncyclopedia": "Ctrl+4",
        "searchCommandBibleLocation": "Ctrl+9",
        "searchCommandBibleName": "Ctrl+8",
        "searchCommandBibleTopic": "Ctrl+6",
        "searchCommandBookNote": "Ctrl+S, 1",
        "searchCommandChapterNote": "Ctrl+S, 2",
        "searchCommandLexicon": "Ctrl+0",
        "searchCommandVerseNote": "Ctrl+S, 3",
        "setDefaultFont": "Ctrl+D, F",
        "setNoToolBar": "Ctrl+J",
        "showGistWindow": "Ctrl+N, G",
        "smallerFont": "Ctrl+-",
        "studyBack": "Ctrl+{",
        "studyForward": "Ctrl+}",
        "studyHistoryButtonClicked": 'Ctrl+"',
        "studyPageScrollPageDown": "Ctrl+H,8",
        "studyPageScrollPageUp": "Ctrl+H,7",
        "studyPageScrollToTop": "Ctrl+H,6",
        "switchIconSize": "Ctrl+T, I",
        "switchLandscapeMode": "Ctrl+L",
        "topHalfScreenHeight": "Ctrl+S,1",
        "twoThirdWindow": "Ctrl+S,S",
    }

    syntemnoData = {
        "back": "Ctrl+Y, 1",
        "bookFeatures": "Ctrl+L, F",
        "bottomHalfScreenHeight": "Ctrl+W, B",
        "chapterFeatures": "Ctrl+L, H",
        "commentaryRefButtonClicked": "Ctrl+Y",
        "createNewNoteFile": "Ctrl+N, N",
        "cycleInstant": "Ctrl+'",
        "displaySearchAllBookCommand": "Ctrl+S, R",
        "displaySearchBibleCommand": "Ctrl+S, B",
        "displaySearchBibleMenu": "Ctrl+S, M",
        "displaySearchBookCommand": "Ctrl+5",
        "displaySearchHighlightCommand": "Ctrl+S, H",
        "displaySearchStudyBibleCommand": "Ctrl+2",
        "editExternalFileButtonClicked": "Ctrl+N, E",
        "enableInstantButtonClicked": "Ctrl+=",
        "enableParagraphButtonClicked": "Ctrl+D, S",
        "enableSubheadingButtonClicked": "Ctrl+D, P",
        "externalFileButtonClicked": "Ctrl+N, R",
        "forward": "Ctrl+Y, 2",
        "fullsizeWindow": "Ctrl+W,F",
        "gotoFirstChapter": 'Ctrl+<',
        "gotoLastChapter": 'Ctrl+>',
        "hideShowAdditionalToolBar": "Ctrl+T, 2",
        "hideShowLeftToolBar": "Ctrl+T, L",
        "hideShowMainToolBar": "Ctrl+T, 1",
        "hideShowRightToolBar": "Ctrl+T, R",
        "hideShowSecondaryToolBar": "Ctrl+T,3",
        "largerFont": "Ctrl++",
        "leftHalfScreenWidth": "Ctrl+W, L",
        "mainHistoryButtonClicked": "Ctrl+Y, M",
        "mainPageScrollPageDown": 'Ctrl+J',
        "mainPageScrollPageUp": 'Ctrl+K',
        "mainPageScrollToTop": 'Ctrl+7',
        "manageControlPanel": "Ctrl+A, 0",
        "manageRemoteControl": "Ctrl+O",
        "masterCurrentIndex0": None,
        "masterCurrentIndex1": None,
        "masterCurrentIndex2": None,
        "masterCurrentIndex3": None,
        "masterHide": None,
        "nextChapterButton": "Ctrl+)",
        "nextMainBook": 'Ctrl+]',
        "nextMainChapter": 'Ctrl+.',
        "openControlPanelTab0": 'Ctrl+U, B',
        "openControlPanelTab1": 'Ctrl+U, L',
        "openControlPanelTab2": 'Ctrl+U, S',
        "openControlPanelTab3": 'Ctrl+U, H',
        "openMainBookNote": "Ctrl+N, B",
        "openMainChapterNote": "Ctrl+N, C",
        "openMainVerseNote": "Ctrl+N, V",
        "openTextFileDialog": "Ctrl+N, O",
        "parallel": "Ctrl+;",
        "parseContentOnClipboard": "Ctrl+^",
        "previousChapterButton": "Ctrl+(",
        "previousMainBook": 'Ctrl+[',
        "previousMainChapter": "Ctrl+<",
        "quitApp": "Ctrl+Q",
        "reloadCurrentRecord": "Ctrl+D, R",
        "rightHalfScreenWidth": "Ctrl+W, R",
        "runCOMBO": "Ctrl+L, M",
        "runCOMMENTARY": "Ctrl+L, C",
        "runCOMPARE": "Ctrl+S, V",
        "runCROSSREFERENCE": "Ctrl+L, X",
        "runDISCOURSE": "Ctrl+L, D",
        "runINDEX": "Ctrl+.",
        "runKJV2Bible": "Ctrl+B, K",
        "runMAB": "Ctrl+B, 5",
        "runMIB": "Ctrl+B, 2",
        "runMOB": "Ctrl+B, 1",
        "runMPB": "Ctrl+B, 4",
        "runMTB": "Ctrl+B, 3",
        "runTSKE": "Ctrl+L, T",
        "runTransliteralBible": "Ctrl+B, T",
        "runWORDS": "Ctrl+L, W",
        "searchCommandBibleCharacter": "Ctrl+S, C",
        "searchCommandBibleDictionary": "Ctrl+3",
        "searchCommandBibleEncyclopedia": "Ctrl+4",
        "searchCommandBibleLocation": "Ctrl+S, O",
        "searchCommandBibleName": "Ctrl+S, N",
        "searchCommandBibleTopic": "Ctrl+6",
        "searchCommandBookNote": "Ctrl+S, 1",
        "searchCommandChapterNote": "Ctrl+S, 2",
        "searchCommandLexicon": "Ctrl+S, L",
        "searchCommandVerseNote": "Ctrl+S, 3",
        "setDefaultFont": "Ctrl+D, F",
        "setNoToolBar": "Ctrl+T, T",
        "showGistWindow": "Ctrl+N, G",
        "smallerFont": "Ctrl+-",
        "studyBack": "Ctrl+Y, 3",
        "studyForward": "Ctrl+Y, 4",
        "studyHistoryButtonClicked": 'Ctrl+Y, S',
        "studyPageScrollPageDown": 'Ctrl+9',
        "studyPageScrollPageUp": 'Ctrl+0',
        "studyPageScrollToTop": "Ctrl+H,6",
        "switchIconSize": "Ctrl+T, I",
        "switchLandscapeMode": "Ctrl+/",
        "topHalfScreenHeight": "Ctrl+W, T",
        "twoThirdWindow": "Ctrl+W,S",
    }

    @staticmethod
    def setup(name):
        try:
            if name not in ("brachys", "syntemno"):
                filename = "shortcut_" + name + ".py"
                if path.exists(filename) and FileUtil.getLineCount("shortcut.py") < 2:
                    from shutil import copyfile
                    # print("Creating shortcut.py from " + filename)
                    copyfile(filename, "shortcut.py")
        except:
            name = "brachys"

        if name == "brachys":
            ShortcutUtil.create(ShortcutUtil.brachysData)
        elif name == "syntemno":
            ShortcutUtil.create(ShortcutUtil.syntemnoData)
        # print("Using " + name + " shortcut")

    @staticmethod
    def create(data):
        if not path.exists("shortcut.py") or FileUtil.getLineCount("shortcut.py") != len(data):
            # print("Writing shortcut.py file")
            with open("shortcut.py", "w", encoding="utf-8") as fileObj:
                for name in data.keys():
                    value = data[name]
                    fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
                fileObj.close()

    @staticmethod
    def reset():
        # print("Resetting shortcut.py file")
        with open("shortcut.py", "w", encoding="utf-8") as fileObj:
            fileObj.write("")
            fileObj.close()

    @staticmethod
    def keyCode(letter):
        if letter is None:
            return None
        else:
            return Qt.Key_A + ord(letter) - ord("A")

    @staticmethod
    def getListCustomShortcuts():
        return [file[9:-3] for file in glob.glob("shortcut_*.py")]

# Test code
def print_info():
    print("shortcut.py: {0}".format(FileUtil.getLineCount("shortcut.py")))
    print("brachysData: {0}".format(len(ShortcutUtil.brachysData)))
    print("syntemnoData: {0}".format(len(ShortcutUtil.syntemnoData)))

def test_brachys():
    ShortcutUtil.setup("brachys")

def test_syntemno():
    ShortcutUtil.setup("syntemno")

def test_custom():
    print(ShortcutUtil.getListCustomShortcuts())
    # ShortcutUtil.setup("custom")

if __name__ == "__main__":
    print_info()
