import pprint
from os import path

from PySide2.QtCore import Qt

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
    }

    syntemnoData = {
        "back": "Ctrl+Y, 1",
        "bottomHalfScreenHeight": "Ctrl+S,2",
        "commentaryRefButtonClicked": "Ctrl+Y",
        "createNewNoteFile": "Ctrl+N",
        "cycleInstant": "Ctrl+T",
        "displaySearchBibleCommand": "Ctrl+1",
        "displaySearchBookCommand": "Ctrl+5",
        "displaySearchStudyBibleCommand": "Ctrl+2",
        "enableInstantButtonClicked": "Ctrl+=",
        "enableParagraphButtonClicked": "Ctrl+P",
        "forward": "Ctrl+]",
        "fullsizeWindow": "Ctrl+S,F",
        "gotoFirstChapter": 'Ctrl+<',
        "gotoLastChapter": 'Ctrl+>',
        "hideShowAdditionalToolBar": "Ctrl+G",
        "largerFont": "Ctrl++",
        "leftHalfScreenWidth": "Ctrl+S,3",
        "mainHistoryButtonClicked": "Ctrl+Y, M",
        "mainPageScrollPageDown": 'Ctrl+J',
        "mainPageScrollPageUp": 'Ctrl+K',
        "mainPageScrollToTop": 'Ctrl+7',
        "manageControlPanel": "Ctrl+M",
        "manageRemoteControl": "Ctrl+R",
        "masterCurrentIndex0": None,
        "masterCurrentIndex1": None,
        "masterCurrentIndex2": None,
        "masterCurrentIndex3": None,
        "masterHide": None,
        "nextMainBook": 'Ctrl+]',
        "nextMainChapter": 'Ctrl+.',
        "openTextFileDialog": "Ctrl+O",
        "parallel": "Ctrl+W",
        "parseContentOnClipboard": "Ctrl+^",
        "previousMainBook": 'Ctrl+[',
        "previousMainChapter": "Ctrl+<",
        "previousMainChapter": 'Ctrl+,',
        "quitApp": "Ctrl+Q",
        "rightHalfScreenWidth": "Ctrl+S,4",
        "runCOMBO": "Ctrl+K",
        "runCOMMENTARY": "Ctrl+Y",
        "runCOMPARE": "Ctrl+D",
        "runCROSSREFERENCE": "Ctrl+R",
        "runKJV2Bible": "Ctrl+B, K",
        "runINDEX": "Ctrl+.",
        "runMAB": "Ctrl+B, 5",
        "runMIB": "Ctrl+B, 2",
        "runMOB": "Ctrl+B, 1",
        "runMPB": "Ctrl+B, 4",
        "runMTB": "Ctrl+B, 3",
        "runTSKE": "Ctrl+E",
        "runTransliteralBible": "Ctrl+B, T",
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
        "studyPageScrollPageDown": 'Ctrl+9',
        "studyPageScrollPageUp": 'Ctrl+0',
        "studyPageScrollToTop": "Ctrl+H,6",
        "switchLandscapeMode": "Ctrl+L",
        "topHalfScreenHeight": "Ctrl+S,1",
        "twoThirdWindow": "Ctrl+S,S",
    }

    @staticmethod
    def setup(name):

        try:
            if name not in ("brachys", "syntemno"):
                filename = "shortcut_" + name + ".py"
                if path.exists(filename):
                    from shutil import copyfile
                    copyfile(filename, "shortcut.py")
                else:
                    name = "brachys"
        except:
            name = "brachys"

        if name == "brachys":
            print("Using brachys")
            ShortcutUtil.create(ShortcutUtil.brachysData)
        elif name == "syntemno":
            print("Using syntemno")
            ShortcutUtil.create(ShortcutUtil.syntemnoData)

    @staticmethod
    def create(data):
        if not path.exists("shortcut.py"):
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

if __name__ == "__main__":

    ShortcutUtil.setup("syntemno")
