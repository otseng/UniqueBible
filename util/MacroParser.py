import os
import config


class MacroParser:

    macros_dir = "macros"

    def __init__(self, parent):
        self.lines = None
        self.parent = parent

    def parse(self, file):
        config.quitMacro = False
        filename = os.path.join(MacroParser.macros_dir, file)
        if os.path.isfile(filename):
            file = open(filename, "r")
            self.lines = file.readlines()
            currentLine = 0
            while(currentLine < len(self.lines)) and not config.quitMacro:
                currentLine = self.parse_line(currentLine)
            self.parent.closePopover()

    def parse_line(self, currentLine):
        try:
            line = self.lines[currentLine].strip()
            if line.startswith("#") or line.startswith("!") or len(line) == 0:
                pass
            elif line.startswith("config."):
                exec(line)
                pass
            elif line.startswith("."):
                command = line[1:].strip()
                if len(command) > 0:
                    method = command.split(" ")[0]
                    arg_str = command[len(method):]
                    args = arg_str.split(",")
                    if (args[0] == ''):
                        getattr(self.parent, method)()
                    elif (len(args) == 1):
                        getattr(self.parent, method)(args[0].strip())
                    elif (len(args) == 2):
                        getattr(self.parent, method)(args[0].strip(), args[1].strip())
            else:
                self.parent.textCommandLineEdit.setText(line)
                self.parent.runTextCommand(line, forceExecute=True)
        except Exception as e:
            print("Error running line: {0}".format(line))
            print("{0}".format(e))
        currentLine += 1
        return currentLine

