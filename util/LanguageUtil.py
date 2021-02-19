import glob
import importlib
import locale
from os import path

import config
from Languages import Languages
from Translator import Translator


class LanguageUtil:

    @staticmethod
    def getCodesSupportedLanguages():
        files = sorted(glob.glob("lang/language_*.py"))
        return [file[-8:-3] for file in files]

    @staticmethod
    def getNamesSupportedLanguages():
        codes = LanguageUtil.getCodesSupportedLanguages()
        return [Languages.decode[code] for code in codes]

    @staticmethod
    def getSystemDefaultLanguage():
        locale.setlocale(locale.LC_ALL, "")
        return locale.getlocale(locale.LC_MESSAGES)[0]

    @staticmethod
    def determineDefaultLanguage():
        supportedLanguages = LanguageUtil.getCodesSupportedLanguages()
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

    @staticmethod
    def createNewLanguageFile(lang, force=False):
        filename = "lang/language_" + lang + ".py"
        if not force and path.exists(filename):
            print(filename + " already exists")
        else:
            print("Creating " + filename)
            with open(filename, "w", encoding="utf-8") as fileObj:
                fileObj.write("translation = {\n")
                translator = Translator()
                master = LanguageUtil.loadTranslation("en_US")
                count = 0
                for key in master.keys():
                    count += 1
                    if count > 500:
                        break
                    text = master[key]
                    if key in ["menu1_app"]:
                        result = text
                    else:
                        result = translator.translate(text, "en", lang[:2])
                    fileObj.write('    "{0}": "{1}",\n'.format(key, result))
                fileObj.write("}\n")
                fileObj.close()
                print("{0} lines translated".format(count))

# Test code

def test_getCodesSupportedLanguages():
    for lang in LanguageUtil.getCodesSupportedLanguages():
        print(lang)

def test_getNamesSupportedLanguages():
    for lang in LanguageUtil.getNamesSupportedLanguages():
        print(lang)

def test_defaultLanguage():
    print(LanguageUtil.getSystemDefaultLanguage())

def test_loadTranslation():
    print(LanguageUtil.loadTranslation("en_US"))

def validateLanguageFileSizes():
    languages = LanguageUtil.getCodesSupportedLanguages()
    for lang in languages:
        trans = LanguageUtil.loadTranslation(lang)
        print("{0} has size {1}".format(lang, len(trans)))

def compareLanguageFiles(lang1, lang2):
    trans1 = LanguageUtil.loadTranslation(lang1)
    trans2 = LanguageUtil.loadTranslation(lang2)
    for key1 in trans1.keys():
        if key1 not in trans2.keys():
            print("{0} not in {1} : {2}".format(key1, lang2, trans1[key1]))

def createNewLanguageFile(lang, force=False):
    LanguageUtil.createNewLanguageFile(lang, force)

if __name__ == "__main__":

    # test_defaultLanguage()
    # test_getNamesSupportedLanguages()
    # test_loadTranslation()
    # validateLanguageFileSizes()
    # compareLanguageFiles("en_GB", "en_US")
    createNewLanguageFile("ko_KR", True)
