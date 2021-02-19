import glob
import locale
from os import environ


class TranslationUtil:

    @staticmethod
    def getListSupportedLanguages():
        files = sorted(glob.glob("translations/Translation_*.py"))
        return [file[-8:-3] for file in files]


def test_getlistSupportedLanguages():
    for lang in TranslationUtil.getListSupportedLanguages():
        print(lang)

def test_langDetect():
    locale.setlocale(locale.LC_ALL, "")
    print(locale.getlocale(locale.LC_MESSAGES)[0])
    if hasattr(environ, 'LANG'):
        print(environ['LANG'])

if __name__ == "__main__":

    # test_getlistSupportedLanguages()
    test_langDetect()
