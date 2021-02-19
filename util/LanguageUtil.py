import glob
import importlib
import locale

import config


class LanguageUtil:

    @staticmethod
    def getListSupportedLanguages():
        files = sorted(glob.glob("lang/language_*.py"))
        return [file[-8:-3] for file in files]

    @staticmethod
    def getSystemDefaultLanguage():
        locale.setlocale(locale.LC_ALL, "")
        return locale.getlocale(locale.LC_MESSAGES)[0]

    @staticmethod
    def determineDefaultLanguage():
        supportedLanguages = LanguageUtil.getListSupportedLanguages()
        if hasattr(config, "displayLanguage") and config.displayLanguage in supportedLanguages:
            return config.displayLanguage
        systemLang = LanguageUtil.getSystemDefaultLanguage()
        if systemLang in supportedLanguages:
            return systemLang
        else:
            return "en_US"

    @staticmethod
    def loadTranslation(lang):
        file = "lang.language_{0}".format(lang)
        trans = importlib.import_module(file)
        return trans.translation

# Test code

def test_getlistSupportedLanguages():
    for lang in LanguageUtil.getListSupportedLanguages():
        print(lang)

def test_defaultLanguage():
    print(LanguageUtil.getSystemDefaultLanguage())

def test_loadTranslation():
    print(LanguageUtil.loadTranslation("en_US"))

def validateLanguageFileSizes():
    languages = LanguageUtil.getListSupportedLanguages()
    for lang in languages:
        trans = LanguageUtil.loadTranslation(lang)
        print("{0} has size {1}".format(lang, len(trans)))


if __name__ == "__main__":

    # test_defaultLanguage()
    # test_getlistSupportedLanguages()
    # test_loadTranslation()
    validateLanguageFileSizes()
