import logging
import config
from TextCommandParser import TextCommandParser


# [KEYWORD] PRESENT
# Shows passage in window for presentation purposes
# Usage - PRESENT:::[BIBLE_VERSION]:::[BIBLE_REFERENCE(S)]
# Examples:
# PRESENT:::NET:::John 3:16
def presentCommand(command, source):
    logger = logging.getLogger('uba')
    msg = "Present passage {0}:{1}".format(command, source)
    logger.info(msg)
    # config.mainWindow.displayMessage(msg)
    parser = TextCommandParser(config.mainWindow)
    return parser.textAnotherView(command, source, "main")

config.mainWindow.textCommandParser.interpreters["present"] = (presentCommand, "present")
