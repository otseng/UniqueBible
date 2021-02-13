import pprint

from os import path
from PySide2.QtCore import Qt

from util.FileUtil import FileUtil


class ShortcutUtil:

    brachysData = {
        "back": "Ctrl+[",
        "bottomHalfScreenHeight": "Ctrl+S,2",
        "commentaryRefButtonClicked": "Ctrl+Y",
        "createNewNoteFile": "Ctrl+N",
        "cycleInstant": "Ctrl+T",
        "displaySearchBibleCommand": "Ctrl+1",
        "displaySearchBookCommand": "Ctrl+5",
        "displaySearchStudyBibleCommand": "Ctrl+2",
        "enableInstantButtonClicked": "Ctrl+=",
        "enableParagraphButtonClicked": "Ctrl+P",
        "externalFileButtonClicked": "Ctrl+N, R",
        "editExternalFileButtonClicked": "Ctrl+N, E",
        "forward": "Ctrl+]",
        "fullsizeWindow": "Ctrl+S,F",
        "gotoFirstChapter": None,
        "gotoLastChapter": None,
        "hideShowAdditionalToolBar": "Ctrl+G",
        "largerFont": "Ctrl++",
        "leftHalfScreenWidth": "Ctrl+S,3",
        "mainHistoryButtonClicked": "Ctrl+'",
        "mainPageScrollPageDown": "Ctrl+H,5",
        "mainPageScrollPageUp": "Ctrl+H,4",
        "mainPageScrollToTop": "Ctrl+H,3",
        "manageControlPanel": "Ctrl+M",
        "manageRemoteControl": "Ctrl+R",
        "masterCurrentIndex0": 'B',
        "masterCurrentIndex1": 'L',
        "masterCurrentIndex2": 'F',
        "masterCurrentIndex3": 'H',
        "masterHide": 'H',
        "nextMainBook": "Ctrl+H,1",
        "nextMainChapter": "Ctrl+>",
        "openTextFileDialog": "Ctrl+O",
        "parallel": "Ctrl+W",
        "parseContentOnClipboard": "Ctrl+^",
        "previousMainBook": "Ctrl+H,2",
        "previousMainChapter": "Ctrl+<",
        "quitApp": "Ctrl+Q",
        "rightHalfScreenWidth": "Ctrl+S,4",
        "runCOMBO": "Ctrl+K",
        "runCOMMENTARY": "Ctrl+Y",
        "runCOMPARE": "Ctrl+D",
        "runCROSSREFERENCE": "Ctrl+R",
        "runINDEX": "Ctrl+.",
        "runMAB": "Ctrl+B, 5",
        "runMIB": "Ctrl+B, 2",
        "runMOB": "Ctrl+B, 1",
        "runMPB": "Ctrl+B, 4",
        "runMTB": "Ctrl+B, 3",
        "runTSKE": "Ctrl+E",
        "searchCommandBibleCharacter": "Ctrl+7",
        "searchCommandBibleDictionary": "Ctrl+3",
        "searchCommandBibleEncyclopedia": "Ctrl+4",
        "searchCommandBibleLocation": "Ctrl+9",
        "searchCommandBibleName": "Ctrl+8",
        "searchCommandBibleTopic": "Ctrl+6",
        "searchCommandLexicon": "Ctrl+0",
        "setNoToolBar": "Ctrl+J",
        "smallerFont": "Ctrl+-",
        "studyBack": "Ctrl+{",
        "studyForward": "Ctrl+}",
        "studyHistoryButtonClicked": 'Ctrl+"',
        "studyPageScrollPageDown": "Ctrl+H,8",
        "studyPageScrollPageUp": "Ctrl+H,7",
        "studyPageScrollToTop": "Ctrl+H,6",
        "switchLandscapeMode": "Ctrl+L",
        "topHalfScreenHeight": "Ctrl+S,1",
        "twoThirdWindow": "Ctrl+S,S",
        "runTransliteralBible": None,
        "runKJV2Bible": None,
        "displaySearchBibleMenu": "Ctrl+S, M",
        "openMainBookNote": "Ctrl+N, B",
        "runWORDS": "Ctrl+L, W",
        "runDISCOURSE": "Ctrl+L, D",
        "bookFeatures": "Ctrl+L, F",
        "chapterFeatures": "Ctrl+L, H",
        "setDefaultFont": "Ctrl+D, F",
        "switchIconSize": "Ctrl+T, I",
        "hideShowLeftToolBar": "Ctrl+T, L",
        "hideShowRightToolBar": "Ctrl+T, R",
        "hideShowMainToolBar": "Ctrl+T, 1",
        "previousChapterButton": "Ctrl+(",
        "reloadCurrentRecord": "Ctrl+D, R",
        "nextChapterButton": "Ctrl+)",
        "openMainChapterNote": "Ctrl+N, C",
        "openMainVerseNote": "Ctrl+N, V",
        "searchCommandBookNote": "Ctrl+S, 1",
        "searchCommandChapterNote": "Ctrl+S, 2",
        "searchCommandVerseNote": "Ctrl+S, 3",
        "showGistWindow": "Ctrl+N, G",
        "hideShowSecondaryToolBar": "Ctrl+T,3",
        "enableSubheadingButtonClicked": "Ctrl+D, P",
        "displaySearchAllBookCommand": "Ctrl+S, R",
        "displaySearchHighlightCommand": "Ctrl+S, H",
    }

    syntemnoData = {
        "back": "Ctrl+Y, 1",
        "bottomHalfScreenHeight": "Ctrl+W, B",
        "bookFeatures": "Ctrl+L, F",
        "chapterFeatures": "Ctrl+L, H",
        "commentaryRefButtonClicked": "Ctrl+Y",
        "createNewNoteFile": "Ctrl+N, N",
        "cycleInstant": "Ctrl+'",
        "displaySearchBibleCommand": "Ctrl+S, B",
        "displaySearchBibleMenu": "Ctrl+S, M",
        "displaySearchHighlightCommand": "Ctrl+S, H",
        "displaySearchBookCommand": "Ctrl+5",
        "displaySearchStudyBibleCommand": "Ctrl+2",
        "displaySearchAllBookCommand": "Ctrl+S, R",
        "enableInstantButtonClicked": "Ctrl+=",
        "editExternalFileButtonClicked": "Ctrl+N, E",
        "enableParagraphButtonClicked": "Ctrl+D, S",
        "enableSubheadingButtonClicked": "Ctrl+D, P",
        "externalFileButtonClicked": "Ctrl+N, R",
        "forward": "Ctrl+Y, 2",
        "fullsizeWindow": "Ctrl+W,F",
        "gotoFirstChapter": 'Ctrl+<',
        "gotoLastChapter": 'Ctrl+>',
        "hideShowRightToolBar": "Ctrl+T, R",
        "hideShowMainToolBar": "Ctrl+T, 1",
        "hideShowSecondaryToolBar": "Ctrl+T,3",
        "hideShowAdditionalToolBar": "Ctrl+T, 2",
        "largerFont": "Ctrl++",
        "leftHalfScreenWidth": "Ctrl+W, L",
        "mainHistoryButtonClicked": "Ctrl+Y, M",
        "mainPageScrollPageDown": 'Ctrl+J',
        "mainPageScrollPageUp": 'Ctrl+K',
        "mainPageScrollToTop": 'Ctrl+7',
        "manageControlPanel": "Ctrl+A",
        "manageRemoteControl": "Ctrl+O",
        "masterCurrentIndex0": None,
        "masterCurrentIndex1": None,
        "masterCurrentIndex2": None,
        "masterCurrentIndex3": None,
        "masterHide": None,
        "nextChapterButton": "Ctrl+)",
        "nextMainBook": 'Ctrl+]',
        "nextMainChapter": 'Ctrl+.',
        "openTextFileDialog": "Ctrl+N, O",
        "openMainBookNote": "Ctrl+N, B",
        "openMainChapterNote": "Ctrl+N, C",
        "openMainVerseNote": "Ctrl+N, V",
        "parallel": "Ctrl+;",
        "parseContentOnClipboard": "Ctrl+^",
        "previousMainBook": 'Ctrl+[',
        "previousChapterButton": "Ctrl+(",
        "previousMainChapter": "Ctrl+<",
        "previousMainChapter": 'Ctrl+,',
        "quitApp": "Ctrl+Q",
        "reloadCurrentRecord": "Ctrl+D, R",
        "rightHalfScreenWidth": "Ctrl+W, R",
        "runCOMBO": "Ctrl+L, M",
        "runCOMMENTARY": "Ctrl+L, C",
        "runCOMPARE": "Ctrl+S, V",
        "runCROSSREFERENCE": "Ctrl+L, X",
        "runKJV2Bible": "Ctrl+B, K",
        "runINDEX": "Ctrl+.",
        "runDISCOURSE": "Ctrl+L, D",
        "runMAB": "Ctrl+B, 5",
        "runMIB": "Ctrl+B, 2",
        "runMOB": "Ctrl+B, 1",
        "runMPB": "Ctrl+B, 4",
        "runMTB": "Ctrl+B, 3",
        "runTSKE": "Ctrl+L, T",
        "runWORDS": "Ctrl+L, W",
        "runTransliteralBible": "Ctrl+B, T",
        "searchCommandBookNote": "Ctrl+S, 1",
        "searchCommandChapterNote": "Ctrl+S, 2",
        "searchCommandVerseNote": "Ctrl+S, 3",
        "searchCommandBibleCharacter": "Ctrl+S, C",
        "searchCommandBibleDictionary": "Ctrl+3",
        "searchCommandBibleEncyclopedia": "Ctrl+4",
        "searchCommandBibleLocation": "Ctrl+S, O",
        "searchCommandBibleName": "Ctrl+S, N",
        "searchCommandBibleTopic": "Ctrl+6",
        "searchCommandLexicon": "Ctrl+S, L",
        "setNoToolBar": "Ctrl+T, T",
        "showGistWindow": "Ctrl+N, G",
        "hideShowLeftToolBar": "Ctrl+T, L",
        "smallerFont": "Ctrl+-",
        "setDefaultFont": "Ctrl+D, F",
        "studyBack": "Ctrl+Y, 3",
        "studyForward": "Ctrl+Y, 4",
        "studyHistoryButtonClicked": 'Ctrl+Y, S',
        "studyPageScrollPageDown": 'Ctrl+9',
        "studyPageScrollPageUp": 'Ctrl+0',
        "switchIconSize": "Ctrl+T, I",
        "studyPageScrollToTop": "Ctrl+H,6",
        "switchLandscapeMode": "Ctrl+/",
        "topHalfScreenHeight": "Ctrl+W, T",
        "twoThirdWindow": "Ctrl+W,S",
    }

    @staticmethod
    def setup(name):
        try:
            if name not in ("brachys", "syntemno"):
                filename = "shortcut_" + name + ".py"
                if path.exists(filename) and not path.exists("shortcut.py"):
                    from shutil import copyfile
                    print("Creating shortcut.py from " + filename)
                    copyfile(filename, "shortcut.py")
        except:
            name = "brachys"

        if name == "brachys":
            ShortcutUtil.create(ShortcutUtil.brachysData)
        elif name == "syntemno":
            ShortcutUtil.create(ShortcutUtil.syntemnoData)
        print("Using " + name + " shortcut")

    @staticmethod
    def create(data):
        if not path.exists("shortcut.py") or FileUtil.getLineCount("shortcut.py") != len(data):
            print("Writing shortcut.py file")
            with open("shortcut.py", "w", encoding="utf-8") as fileObj:
                for name in data.keys():
                    value = data[name]
                    fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
            fileObj.close()

    @staticmethod
    def keyCode(letter):
        if letter is None:
            return None
        else:
            return Qt.Key_A + ord(letter) - ord("A")


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
    ShortcutUtil.setup("custom")

if __name__ == "__main__":
    test_brachys()
    print_info()
