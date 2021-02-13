import shortcut


class ShortcutUtil:

    focusData = {
        "createNewNoteFile": "Ctrl+N",
        "openTextFileDialog": "Ctrl+O",
        "largerFont": "Ctrl++",
        "smallerFont": "Ctrl+-",
        "fullsizeWindow": "Ctrl+S,F",
        "topHalfScreenHeight": "Ctrl+S,1",
        "bottomHalfScreenHeight": "Ctrl+S,2",
        "leftHalfScreenWidth": "Ctrl+S,3",
        "rightHalfScreenWidth": "Ctrl+S,4",
        "setNoToolBar": "Ctrl+J",
        "hideShowAdditionalToolBar": "Ctrl+G",
        "parallel": "Ctrl+W",
        "cycleInstant": "Ctrl+T",
        "parseContentOnClipboard": "Ctrl+^",
        "quitApp": "Ctrl+Q",
        "nextMainBook": "Ctrl+H,1",
        "previousMainBook": "Ctrl+H,2",
        "nextMainChapter": "Ctrl+>",
        "previousMainChapter": "Ctrl+<",
        "mainPageScrollToTop": "Ctrl+H,3",
        "mainPageScrollPageUp": "Ctrl+H,4",
        "mainPageScrollPageDown": "Ctrl+H,5",
        "studyPageScrollToTop": "Ctrl+H,6",
        "studyPageScrollPageUp": "Ctrl+H,7",
        "studyPageScrollPageDown": "Ctrl+H,8",

    }

    @staticmethod
    def setup():
        if not hasattr(shortcut, "createNewNoteFile"):
            ShortcutUtil.create(ShortcutUtil.focusData)

    @staticmethod
    def create(data):
        with open("shortcut.py", "w", encoding="utf-8") as fileObj:
            for name in data.keys():
                value = data[name]
                fileObj.write("{0} = \"{1}\"\n".format(name, value))
                setattr(shortcut, name, value)
        fileObj.close()


if __name__ == "__main__":

    ShortcutUtil.create()
