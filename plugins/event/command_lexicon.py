import html
import os
import re

import config

if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QThread
    from PySide6.QtGui import QClipboard
else:
    from qtpy.QtWidgets import QApplication
    from qtpy.QtCore import QThread
    from qtpy.QtGui import QClipboard

if ":::" in config.eventCommand:
    commandList = config.eventCommand.split(":::")
    strongs = commandList[1].lower().strip()

    hebrew = False
    greek = False
    first = strongs[0]
    if (first == 'h'):
        hebrew = True
    elif (first == 'h'):
        greek = True
    else:
        first = 'g'
        greek = True
    results = re.findall(r'\d+', strongs)
    if results:
        number = results[0]

    TRLIT_DIR = "/home/oliver/dev/transliteral_bible"
    file = TRLIT_DIR + "/strongs/" + first + "/" + first + number + ".md"
    if os.path.isfile(file):
        with open(file, 'r') as myfile:
            filedata = myfile.read()
        re_transliteral = re.compile(r'\[(.*)\]\(https:\/\/www.blueletterbible.org')
        s_transliteral = html.unescape(re_transliteral.search(filedata).group(1))
        s_transliteral = s_transliteral.replace('`', "'")
        output = "[" + s_transliteral + "](../" + file + ")"
        output = output.replace(TRLIT_DIR, "")
        output = output.replace("//", "/../")
        QApplication.clipboard().setText(output)
        QApplication.clipboard().setText(output, QClipboard.Selection)
        QApplication.clipboard().setText(output, QClipboard.Clipboard)
        print("Exists: " + file)
    else:
        print("Need to create!!! " + file)


