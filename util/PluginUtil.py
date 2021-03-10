import glob
import os
from pathlib import Path


class PluginUtil:

    @staticmethod
    def getLayouts():
        pattern = os.path.join(os.getcwd(), "plugins", "layout", "*.py")
        print(pattern)
        files = [Path(file).stem for file in glob.glob(pattern)]
        return files

if __name__ == '__main__':

    print(PluginUtil.getLayouts())
