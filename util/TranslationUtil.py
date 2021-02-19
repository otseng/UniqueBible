import glob
import locale
from os import environ


class TranslationUtil:

    @staticmethod
    def getListSupportedLanguages():
        files = sorted(glob.glob("translations/Translation_*.py"))
        return [file[-8:-3] for file in files]

    @staticmethod
    def getSystemDefaultLanguage():
        locale.setlocale(locale.LC_ALL, "")
        return locale.getlocale(locale.LC_MESSAGES)[0]


def test_getlistSupportedLanguages():
    for lang in TranslationUtil.getListSupportedLanguages():
        print(lang)

def test_defaultLanguage():
    print(TranslationUtil.getSystemDefaultLanguage())

if __name__ == "__main__":

    # test_getlistSupportedLanguages()
    test_defaultLanguage()
