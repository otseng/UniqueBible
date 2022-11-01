#!/usr/bin/env python

import config
from util.text_editor_checkup import *
import argparse, sys, os
from util.TextEditorUtility import TextEditorUtility
from util.terminal_text_editor import TextEditor


class StartEditor:

    def multilineEditor(self, text="", placeholder="", filepath="", newFile=False, wd=""):
        config.textEditor = TextEditor(config.mainWindow, working_directory=wd)
        if newFile:
            return config.textEditor.newFile()
        elif filepath:
            return config.textEditor.openFile(filepath)
        return config.textEditor.multilineEditor(text, placeholder)

if __name__ == "__main__":
    # make sure relative path of plugins folder works
    thisFile = os.path.realpath(__file__)
    wd = os.path.dirname(thisFile)

    # make utilities available to plugins
    config.mainWindow = TextEditorUtility(working_directory=wd)

    # startup
    startup = StartEditor()

    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('--filename', '-f', nargs='?')
    parser.add_argument('--text', '-t', nargs='?')
    args = parser.parse_args()
    if args.file:
        startup.multilineEditor(filepath=args.file, wd=wd)
    elif args.filename:
        startup.multilineEditor(filepath=args.filename, wd=wd)
    elif args.text:
        startup.multilineEditor(text=args.text, wd=wd)
    elif not sys.stdin.isatty():
        #text = sys.stdin.read()
        #startup.multilineEditor(text=text, wd=wd)
        parser.print_help()
    else:
        startup.multilineEditor(newFile=True, wd=wd)
