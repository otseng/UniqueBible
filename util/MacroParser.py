import os

class MacroParser:

    macros_dir = "macros"

    def __init__(self):
        self.lines = None

    def parse(self, main, file):
        filename = os.path.join(MacroParser.macros_dir, file)
        if os.path.isfile(filename):
            file = open(filename, "r")
            self.lines = file.readlines()
            currentLine = 0
            while(currentLine < len(self.lines)):
                currentLine = self.parse_line(main, currentLine)
            main.closePopover()

    def parse_line(self, main, currentLine):
        try:
            line = self.lines[currentLine].strip()
            if line.startswith("#") or line.startswith("!") or len(line) == 0:
                pass
            elif line.startswith("."):
                command = line[1:].strip()
                if len(command) > 0:
                    method = command.split(" ")[0]
                    arg_str = command[len(method):]
                    args = arg_str.split(",")
                    if (args[0] == ''):
                        getattr(main, method)()
                    elif (len(args) == 1):
                        getattr(main, method)(args[0].strip())
                    elif (len(args) == 2):
                        getattr(main, method)(args[0].strip(), args[1].strip())
            else:
                main.textCommandLineEdit.setText(line)
                main.runTextCommand(line, forceExecute=True)
        except Exception as e:
            print("Error running line: {0}".format(line))
            print("{0}".format(e))
        currentLine += 1
        return currentLine

