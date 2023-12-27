import config
from util.BibleBooks import BibleBooks

text = str(config.mainText)
if text[-1] not in ('+', '*', 'x'):
    text = "KJVx"
book = BibleBooks.abbrev["eng"][str(config.mainB)][0]

config.mainWindow.runTextCommand("HIGHLIGHTWORDFREQUENCY:::{0}:::{1} {2}".format(text, book, config.mainC))
