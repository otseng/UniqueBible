import glob
import pprint

from os import path
from PySide2.QtCore import Qt

import config
from util.FileUtil import FileUtil


# 2 defined sets of shortcuts:
# brachys
# syntemno
class ShortcutUtil:
    brachysData = {
        "back": "Ctrl+[",
        "bookFeatures": "Ctrl+R, F",
        "bottomHalfScreenHeight": "Ctrl+S, 2",
        "chapterFeatures": "Ctrl+W, H",
        "commentaryRefButtonClicked": "Ctrl+H, C",
        "createNewNoteFile": "Ctrl+N, N",
        "cycleInstant": "Ctrl+U, 0",
        "displaySearchAllBookCommand": "Ctrl+S, R",
        "displaySearchBibleCommand": "Ctrl+1",
        "displaySearchBibleMenu": "Ctrl+S, M",
        "displaySearchBookCommand": "Ctrl+E, 5",
        "displaySearchHighlightCommand": "Ctrl+S, H",
        "displaySearchStudyBibleCommand": "Ctrl+E, 1",
        "editExternalFileButtonClicked": "Ctrl+N, E",
        "enableInstantButtonClicked": "Ctrl+=",
        "enableParagraphButtonClicked": "Ctrl+P",
        "enableSubheadingButtonClicked": "Ctrl+D, P",
        "externalFileButtonClicked": "Ctrl+N, R",
        "forward": "Ctrl+]",
        "fullsizeWindow": "Ctrl+S, F",
        "gotoFirstChapter": "Ctrl+I, <",
        "gotoLastChapter": "Ctrl+I, >",
        "hideShowSideToolBars": "Ctrl+E, \\",
        "hideShowAdditionalToolBar": "Ctrl+H, 1",
        "hideShowLeftToolBar": "Ctrl+T, L",
        "hideShowMainToolBar": "Ctrl+T, 1",
        "hideShowRightToolBar": "Ctrl+T, R",
        "hideShowSecondaryToolBar": "Ctrl+T, 3",
        "largerFont": "Ctrl++",
        "leftHalfScreenWidth": "Ctrl+S, 3",
        "mainHistoryButtonClicked": "Ctrl+'",
        "mainPageScrollPageDown": "Ctrl+H, 5",
        "mainPageScrollPageUp": "Ctrl+H, 4",
        "mainPageScrollToTop": "Ctrl+H, 3",
        "manageControlPanel": "Ctrl+M, 0",
        "manageRemoteControl": "Ctrl+I, R",
        "masterCurrentIndex0": "Ctrl+B",
        "masterCurrentIndex1": "Ctrl+L",
        "masterCurrentIndex2": "Ctrl+F",
        "masterCurrentIndex3": "Ctrl+Y",
        "masterHideKeyCode": 'Z',
        "nextChapterButton": "Ctrl+)",
        "nextMainBook": "Ctrl+}",
        "nextMainChapter": "Ctrl+>",
        "openControlPanelTab0": 'Ctrl+B',
        "openControlPanelTab1": 'Ctrl+L',
        "openControlPanelTab2": 'Ctrl+F',
        "openControlPanelTab3": 'Ctrl+Y',
        "openControlPanelTab4": 'Ctrl+M',
        "openMainBookNote": "Ctrl+N, B",
        "openMainChapterNote": "Ctrl+N, C",
        "openMainVerseNote": "Ctrl+N, V",
        "openTextFileDialog": "Ctrl+O",
        "parallel": "Ctrl+W",
        "parseContentOnClipboard": "Ctrl+^",
        "previousChapterButton": "Ctrl+(",
        "previousMainBook": "Ctrl+{",
        "previousMainChapter": "Ctrl+<",
        "quitApp": "Ctrl+Q",
        "reloadCurrentRecord": "Ctrl+D, R",
        "rightHalfScreenWidth": "Ctrl+S, 4",
        "runCOMBO": "Ctrl+K",
        "runCOMMENTARY": "Ctrl+I, C",
        "runCOMPARE": "Ctrl+D, C",
        "runCROSSREFERENCE": "Ctrl+U, C",
        "runDISCOURSE": "Ctrl+R, D",
        "runINDEX": "Ctrl+.",
        "runKJV2Bible": "Ctrl+I, K",
        "runMAB": "Ctrl+M, 1",
        "runMIB": "Ctrl+M, 2",
        "runMOB": "Ctrl+M, 3",
        "runMPB": "Ctrl+M, 4",
        "runMTB": "Ctrl+M, 5",
        "runTSKE": "Ctrl+M, T",
        "runTransliteralBible": "Ctrl+I, T",
        "runWORDS": "Ctrl+R, W",
        "searchCommandBibleCharacter": "Ctrl+E, 7",
        "searchCommandBibleDictionary": "Ctrl+E, 2",
        "searchCommandBibleEncyclopedia": "Ctrl+E, 3",
        "searchCommandBibleLocation": "Ctrl+E, 9",
        "searchCommandBibleName": "Ctrl+E, 8",
        "searchCommandBibleTopic": "Ctrl+E, 6",
        "searchCommandBookNote": "Ctrl+S, 1",
        "searchCommandChapterNote": "Ctrl+S, 2",
        "searchCommandLexicon": "Ctrl+S, 0",
        "searchCommandVerseNote": "Ctrl+S, 3",
        "setDefaultFont": "Ctrl+D, F",
        "setNoToolBar": "Ctrl+J",
        "showGistWindow": "Ctrl+N, G",
        "smallerFont": "Ctrl+-",
        "studyBack": "Ctrl+I, [",
        "studyForward": "Ctrl+I, ]",
        "studyHistoryButtonClicked": 'Ctrl+"',
        "studyPageScrollPageDown": "Ctrl+H, 8",
        "studyPageScrollPageUp": "Ctrl+H, 7",
        "studyPageScrollToTop": "Ctrl+H, 6",
        "switchIconSize": "Ctrl+T, I",
        "switchLandscapeMode": "Ctrl+R, M",
        "toggleHighlightMarker": "Ctrl+I, I",
        "topHalfScreenHeight": "Ctrl+S, 1",
        "twoThirdWindow": "Ctrl+S, S",
    }

    syntemnoData = {
        "back": "Ctrl+Y, 1",
        "bookFeatures": "Ctrl+L, F",
        "bottomHalfScreenHeight": "Ctrl+W, B",
        "chapterFeatures": "Ctrl+L, H",
        "commentaryRefButtonClicked": "Ctrl+I, C",
        "createNewNoteFile": "Ctrl+N, N",
        "cycleInstant": "Ctrl+'",
        "displaySearchAllBookCommand": "Ctrl+S, R",
        "displaySearchBibleCommand": "Ctrl+S, B",
        "displaySearchBibleMenu": "Ctrl+S, M",
        "displaySearchBookCommand": "Ctrl+E, 5",
        "displaySearchHighlightCommand": "Ctrl+S, H",
        "displaySearchStudyBibleCommand": "Ctrl+E, 2",
        "editExternalFileButtonClicked": "Ctrl+N, E",
        "enableInstantButtonClicked": "Ctrl+=",
        "enableParagraphButtonClicked": "Ctrl+D, S",
        "enableSubheadingButtonClicked": "Ctrl+D, P",
        "externalFileButtonClicked": "Ctrl+N, R",
        "forward": "Ctrl+Y, 2",
        "fullsizeWindow": "Ctrl+W, F",
        "gotoFirstChapter": 'Ctrl+<',
        "gotoLastChapter": 'Ctrl+>',
        "hideShowSideToolBars": "Ctrl+\\",
        "hideShowAdditionalToolBar": "Ctrl+T, 2",
        "hideShowLeftToolBar": "Ctrl+T, L",
        "hideShowMainToolBar": "Ctrl+T, 1",
        "hideShowRightToolBar": "Ctrl+T, R",
        "hideShowSecondaryToolBar": "Ctrl+T, 3",
        "largerFont": "Ctrl++",
        "leftHalfScreenWidth": "Ctrl+W, L",
        "mainHistoryButtonClicked": "Ctrl+Y, M",
        "mainPageScrollPageDown": 'Ctrl+J',
        "mainPageScrollPageUp": 'Ctrl+K',
        "mainPageScrollToTop": 'Ctrl+7',
        "manageControlPanel": "Ctrl+U, 0",
        "manageRemoteControl": "Ctrl+O",
        "masterCurrentIndex0": "Ctrl+U, B",
        "masterCurrentIndex1": "Ctrl+U, L",
        "masterCurrentIndex2": "Ctrl+U, F",
        "masterCurrentIndex3": "Ctrl+U, Y",
        "masterCurrentIndex4": "Ctrl+U, M",
        "masterHideKeyCode": "Z",
        "nextChapterButton": "Ctrl+)",
        "nextMainBook": 'Ctrl+]',
        "nextMainChapter": 'Ctrl+.',
        "openControlPanelTab0": 'Ctrl+U, B',
        "openControlPanelTab1": 'Ctrl+U, L',
        "openControlPanelTab2": 'Ctrl+U, S',
        "openControlPanelTab3": 'Ctrl+U, Y',
        "openMainBookNote": "Ctrl+N, B",
        "openMainChapterNote": "Ctrl+N, C",
        "openMainVerseNote": "Ctrl+N, V",
        "openTextFileDialog": "Ctrl+N, O",
        "parallel": "Ctrl+;",
        "parseContentOnClipboard": "Ctrl+^",
        "previousChapterButton": "Ctrl+(",
        "previousMainBook": 'Ctrl+[',
        "previousMainChapter": "Ctrl+,",
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
        "searchCommandBibleDictionary": "Ctrl+E, 3",
        "searchCommandBibleEncyclopedia": "Ctrl+E, 4",
        "searchCommandBibleLocation": "Ctrl+S, O",
        "searchCommandBibleName": "Ctrl+S, N",
        "searchCommandBibleTopic": "Ctrl+E, 6",
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
        "studyPageScrollToTop": "Ctrl+8",
        "switchIconSize": "Ctrl+T, I",
        "switchLandscapeMode": "Ctrl+/",
        "toggleHighlightMarker": "Ctrl+I, I",
        "topHalfScreenHeight": "Ctrl+W, T",
        "twoThirdWindow": "Ctrl+W, S",
    }

    @staticmethod
    def setup(name):
        try:
            if name not in ("brachys", "syntemno"):
                filename = "shortcut_" + name + ".py"
                if not path.exists(filename):
                    name = "brachys"
                elif FileUtil.getLineCount("shortcut.py") < 2:
                    from shutil import copyfile
                    copyfile(filename, "shortcut.py")
        except Exception as e:
            name = "brachys"

        if name == "brachys":
            ShortcutUtil.create(ShortcutUtil.brachysData)
        elif name == "syntemno":
            ShortcutUtil.create(ShortcutUtil.syntemnoData)
        config.menuShortcuts = name

    @staticmethod
    def create(data):
        if not path.exists("shortcut.py") or FileUtil.getLineCount("shortcut.py") != len(data):
            with open("shortcut.py", "w", encoding="utf-8") as fileObj:
                for name in data.keys():
                    value = data[name]
                    fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
                fileObj.close()

    @staticmethod
    def reset():
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

    @staticmethod
    def printAllShortcuts():
        import shortcut as sc

        lines = []
        for key in sc.__dict__.keys():
            if key[:1] != '_':
                lines.append(str(sc.__dict__[key]) + " : " + key)
        lines.sort()
        return ("\n".join(lines))


# Test code
def print_info():
    print("shortcut.py: {0}".format(FileUtil.getLineCount("shortcut.py")))
    print("brachysData: {0}".format(len(ShortcutUtil.brachysData)))
    print("syntemnoData: {0}".format(len(ShortcutUtil.syntemnoData)))

def print_brachysData():
    lines = []
    for key in ShortcutUtil.brachysData.keys():
        lines.append(str(ShortcutUtil.brachysData[key]) + " : " + key)
    lines.sort()
    print("\n".join(lines))

def print_syntemnoData():
    lines = []
    for key in ShortcutUtil.syntemnoData.keys():
        lines.append(str(ShortcutUtil.syntemnoData[key]) + " : " + key)
    lines.sort()
    print("\n".join(lines))

def test_brachys():
    ShortcutUtil.setup("brachys")

def test_syntemno():
    ShortcutUtil.setup("syntemno")

def test_custom():
    print(ShortcutUtil.getListCustomShortcuts())
    # ShortcutUtil.setup("custom")

def test_printAllShortcuts():
    print(ShortcutUtil.printAllShortcuts())


if __name__ == "__main__":
    # print_brachysData()
    # print_syntemnoData()
    print_info()
