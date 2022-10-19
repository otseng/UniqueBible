from genericpath import isfile
import re, config, pprint, os, requests, platform, pydoc, markdown, sys, subprocess, json, shutil
from functools import partial
from datetime import date
from pathlib import Path
#import urllib.request
from ast import literal_eval
from db.BiblesSqlite import Bible
from db.JournalSqlite import JournalSqlite
from db.ToolsSqlite import Book
from db.NoteSqlite import NoteSqlite
from util.Languages import Languages
from util.readings import allDays
from util.DateUtil import DateUtil
from util.TextUtil import TextUtil
from util.NetworkUtil import NetworkUtil
from util.RemoteCliMainWindow import RemoteCliMainWindow
from util.TextCommandParser import TextCommandParser
from util.BibleVerseParser import BibleVerseParser
from util.CrossPlatform import CrossPlatform
from util.BibleBooks import BibleBooks
from util.GitHubRepoInfo import GitHubRepoInfo
from util.FileUtil import FileUtil
from util.UpdateUtil import UpdateUtil
from util.DateUtil import DateUtil
from util.WebtopUtil import WebtopUtil
from util.Translator import Translator
from util.HBN import HBN


class LocalCliHandler:

    def __init__(self, command="John 3:16"):
        if config.terminalUseMarvelDataPrivate:
            config.defaultMarvelData = config.marvelData
            config.marvelData = config.marvelDataPrivate
        self.textCommandParser = TextCommandParser(RemoteCliMainWindow())
        self.crossPlatform = CrossPlatform()
        self.crossPlatform.setupResourceLists()
        self.html = "<ref >Unique Bible App</ref>"
        self.plainText = "Unique Bible App"
        self.command = command
        self.dotCommands = self.getDotCommands()
        self.addShortcuts()
        self.initPromptElements()
        self.setOsOpenCmd()
        self.ttsLanguages = self.getTtsLanguages()
        self.ttsLanguageCodes = list(self.ttsLanguages.keys())
        self.bibleBooks = BibleBooks()
        abbReferences, bcvReferences = self.bibleBooks.getAllKJVreferences()
        self.allKJVreferences = self.getDummyDict(abbReferences, ",")
        self.allKJVreferencesBcv1 = self.getDummyDict(bcvReferences)
        self.allKJVreferencesBcv2 = self.getDummyDict(bcvReferences, ":::")
        self.unsupportedCommands = ["_mc", "_mastercontrol", "epub", "anypdf", "searchpdf", "pdffind", "pdf", "docx", "_savepdfcurrentpage", "searchallbookspdf", "readbible", "searchhighlight", "parallel", "_editfile", "_openfile", "_uba", "opennote", "_history", "_historyrecord", "_highlight"]
        if not WebtopUtil.isPackageInstalled("w3m"):
            self.unsupportedCommands.append("sidebyside")
        self.ttsCommandKeyword = self.getDefaultTtsKeyword().lower()
        self.unsupportedCommands.append("gtts" if self.ttsCommandKeyword == "speak" else "speak")
        self.startupException1 = [config.terminal_cancel_action, ".quit", ".q", ".restart", ".z", ".togglepager", ".filters", ".toggleclipboardmonitor", ".history", ".update", ".find", ".sa", ".sas", ".read", ".readsync", ".download", ".paste", ".share", ".copy", ".copyhtml", ".nano", ".vi", ".vim", ".searchbible", ".starthttpserver", ".downloadyoutube", ".web", ".gtts", ".buildportablepython"]
        self.startupException2 = "^(_setconfig:::|\.edit|\.change|\.toggle|\.stop|\.exec|mp3:::|mp4:::|cmd:::|\.backup|\.restore|gtts:::|speak:::|download:::|read:::|readsync:::)"
        #config.cliTtsProcess = None
        config.audio_playing_file = os.path.join("temp", "000_audio_playing.txt")

    # Set text-to-speech default language
    def getTtsLanguages(self):
        # Support Android Google TTS if available
        if config.runMode == "terminal" and config.terminalEnableTermuxAPI:
            config.isGoogleCloudTTSAvailable = True
        if config.isGoogleCloudTTSAvailable and config.ttsDefaultLangauge == "en":
            config.ttsDefaultLangauge = "en-GB"
        return self.crossPlatform.getTtsLanguages()

    def setOsOpenCmd(self):
        if config.terminalEnableTermuxAPI:
            config.open = "termux-open"
        elif platform.system() == "Linux":
            config.open = config.openLinux
        elif platform.system() == "Darwin":
            config.open = config.openMacos
        elif platform.system() == "Windows":
            config.open = config.openWindows

    def initPromptElements(self):
        self.divider = "--------------------"
        self.inputIndicator = ">>> "
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import FileHistory
            from prompt_toolkit.styles import Style
            self.promptStyle = Style.from_dict({
                # User input (default text).
                "": config.terminalCommandEntryColor2,
                # Prompt.
                "indicator": config.terminalPromptIndicatorColor2,
            })
            self.inputIndicator = [
                ("class:indicator", self.inputIndicator),
            ]

            find_history = os.path.join("terminal_history", "find")
            module_history_books = os.path.join("terminal_history", "books")
            module_history_bibles = os.path.join("terminal_history", "bibles")
            module_history_topics = os.path.join("terminal_history", "topics")
            module_history_dictionaries = os.path.join("terminal_history", "dictionaries")
            module_history_encyclopedia = os.path.join("terminal_history", "encyclopedia")
            module_history_lexicons = os.path.join("terminal_history", "lexicons")
            module_history_thirdDict = os.path.join("terminal_history", "thirdPartyDictionaries")
            module_history_commentaries = os.path.join("terminal_history", "commentaries")
            search_bible_history = os.path.join("terminal_history", "search_bible")
            search_strong_bible_history = os.path.join("terminal_history", "search_strong_bible")
            search_bible_book_range_history = os.path.join("terminal_history", "search_bible_book_range")
            config_history = os.path.join("terminal_history", "config")
            live_filter = os.path.join("terminal_history", "live_filter")
            tts_language_history = os.path.join("terminal_history", "tts_language")
            watson_translate_from_language_history = os.path.join("terminal_history", "watson_translate_from_language")
            watson_translate_to_language_history = os.path.join("terminal_history", "watson_translate_to_language")
            google_translate_from_language_history = os.path.join("terminal_history", "google_translate_from_language")
            google_translate_to_language_history = os.path.join("terminal_history", "google_translate_to_language")
            python_string_history = os.path.join("terminal_history", "python_string")
            python_file_history = os.path.join("terminal_history", "python_file")

            self.terminal_live_filter_session = PromptSession(history=FileHistory(live_filter))
            self.terminal_books_selection_session = PromptSession(history=FileHistory(module_history_books))
            self.terminal_find_session = PromptSession(history=FileHistory(find_history))
            self.terminal_search_strong_bible_session = PromptSession(history=FileHistory(search_strong_bible_history))
            self.terminal_search_bible_session = PromptSession(history=FileHistory(search_bible_history))
            self.terminal_search_bible_book_range_session = PromptSession(history=FileHistory(search_bible_book_range_history))
            self.terminal_bible_selection_session = PromptSession(history=FileHistory(module_history_bibles))
            self.terminal_topics_selection_session = PromptSession(history=FileHistory(module_history_topics))
            self.terminal_dictionary_selection_session = PromptSession(history=FileHistory(module_history_dictionaries))
            self.terminal_encyclopedia_selection_session = PromptSession(history=FileHistory(module_history_encyclopedia))
            self.terminal_lexicons_selection_session = PromptSession(history=FileHistory(module_history_lexicons))
            self.terminal_thridPartyDictionaries_selection_session = PromptSession(history=FileHistory(module_history_thirdDict))
            self.terminal_commentary_selection_session = PromptSession(history=FileHistory(module_history_commentaries))
            self.terminal_config_selection_session = PromptSession(history=FileHistory(config_history))
            self.terminal_tts_language_session = PromptSession(history=FileHistory(tts_language_history))
            self.terminal_google_translate_from_language_session = PromptSession(history=FileHistory(google_translate_from_language_history))
            self.terminal_google_translate_to_language_session = PromptSession(history=FileHistory(google_translate_to_language_history))
            self.terminal_python_string_session = PromptSession(history=FileHistory(python_string_history))
            self.terminal_python_file_session = PromptSession(history=FileHistory(python_file_history))
            self.terminal_watson_translate_from_language_session = PromptSession(history=FileHistory(watson_translate_from_language_history))
            self.terminal_watson_translate_to_language_session = PromptSession(history=FileHistory(watson_translate_to_language_history))

        else:

            self.terminal_live_filter_session = None
            self.terminal_watson_translate_from_language_session = None
            self.terminal_watson_translate_to_language_session = None
            self.terminal_google_translate_from_language_session = None
            self.terminal_google_translate_to_language_session = None
            self.terminal_tts_language_session = None
            self.terminal_search_strong_bible_session = None
            self.terminal_books_selection_session = None
            self.terminal_find_session = None
            self.terminal_search_bible_session = None
            self.terminal_search_bible_book_range_session = None
            self.terminal_bible_selection_session = None
            self.terminal_topics_selection_session = None
            self.terminal_dictionary_selection_session = None
            self.terminal_encyclopedia_selection_session = None
            self.terminal_lexicons_selection_session = None
            self.terminal_thridPartyDictionaries_selection_session = None
            self.terminal_commentary_selection_session = None
            self.terminal_config_selection_session = None
            self.terminal_python_string_session = None
            self.terminal_python_file_session = None

    def getShortcuts(self):
        return {
            ".a": config.terminal_dot_a,
            ".b": config.terminal_dot_b,
            ".c": config.terminal_dot_c,
            ".d": config.terminal_dot_d,
            ".e": config.terminal_dot_e,
            ".f": config.terminal_dot_f,
            ".g": config.terminal_dot_g,
            ".h": config.terminal_dot_h,
            ".i": config.terminal_dot_i,
            ".j": config.terminal_dot_j,
            ".k": config.terminal_dot_k,
            ".l": config.terminal_dot_l,
            ".m": config.terminal_dot_m,
            ".n": config.terminal_dot_n,
            ".o": config.terminal_dot_o,
            ".p": config.terminal_dot_p,
            #".q": config.terminal_dot_q,
            ".r": config.terminal_dot_r,
            ".s": config.terminal_dot_s,
            ".t": config.terminal_dot_t,
            ".u": config.terminal_dot_u,
            ".v": config.terminal_dot_v,
            ".w": config.terminal_dot_w,
            ".x": config.terminal_dot_x,
            ".y": config.terminal_dot_y,
            #".z": config.terminal_dot_z,
        }

    def addShortcuts(self):
        for key, value in self.getShortcuts().items():
            value = value.strip()
            if value:
                self.dotCommands[key] = (f"an alias to command '{value}'", partial(self.getContent, value))

    def getDotCommands(self):
        return {
            config.terminal_cancel_action: ("cancel action in current prompt", self.cancelAction),
            ".togglepager": ("toggle paging for text output", self.togglePager),
            ".toggleclipboardmonitor": ("toggle paging for text output", self.toggleClipboardMonitor),
            ".togglebiblecomparison": ("toggle bible comparison view", self.togglebiblecomparison),
            ".togglebiblechapterplainlayout": ("toggle bible chapter plain layout", self.toggleBibleChapterFormat),
            ".toggleplainbiblechaptersubheadings": ("toggle bible chapter subheadings in plain layout", self.toggleaddTitleToPlainChapter),
            ".togglefavouriteverses": ("toggle favourite bible verses in displaying multiple verses", self.toggleaddFavouriteToMultiRef),
            ".togglefavoriteverses": ("an alias to the '.togglefavouriteverses' command", self.toggleaddFavouriteToMultiRef),
            ".toggleversenumberdisplay": ("toggle verse number display", self.toggleshowVerseReference),
            ".toggleusernoteindicator": ("toggle user note indicator display", self.toggleshowUserNoteIndicator),
            ".togglebiblenoteindicator": ("toggle bible note indicator display", self.toggleshowBibleNoteIndicator),
            ".togglebiblelexicalentries": ("toggle lexical entry display", self.togglehideLexicalEntryInBible),
            ".stopaudio": ("stop audio", self.stopAudio),
            ".sa": ("an alias to the '.stopaudio' command", self.stopAudio),
            ".stopaudiosync": ("stop audio with text synchronisation", self.removeAudioPlayingFile),
            ".sas": ("an alias to the '.stopaudiosync' command", self.removeAudioPlayingFile),
            ".read": ("read available audio files", self.read),
            ".readsync": ("read available audio files with text synchronisation", self.readsync),
            ".filters": ("filter text content", self.filters),
            ".run": ("run copied text as command", self.runclipboardtext),
            ".forward": ("open one bible chapter forward", self.forward),
            ".backward": ("open one bible chapter backward", self.backward),
            ".swap": ("swap to a favourite bible", self.swap),
            ".web": ("open web version", self.web),
            ".share": ("copy a web link for sharing", self.share),
            ".tts": ("open text-to-speech feature", lambda: self.tts(False)),
            ".ttscopiedtext": ("run text-to-speech on copied text", self.tts),
            ".ttsc": ("an alias to the '.ttscopiedtext' command", self.tts),
            ".paste": ("display copied text", self.getclipboardtext),
            ".copy": ("copy the last opened content", self.copy),
            ".copyhtml": ("copy the last opened content in html format", self.copyHtml),
            ".quicksearchcopiedtext": ("quick search copied text", self.quickSearch),
            ".qsc": ("an alias to the '.quicksearchcopiedtext' command", self.quickSearch),
            ".quickopencopiedtext": ("quick open copied text", self.quickopen),
            ".qoc": ("an alias to the '.quickopencopiedtext' command", self.quickopen),
            ".quickeditcopiedtext": ("quick edit copied text", self.quickedit),
            ".qec": ("an alias to the '.quickeditcopiedtext' command", self.quickedit),
            ".find": ("find a string in the lastest content", self.find),
            ".findcopiedtext": ("find a string in the copied text", self.findCopiedText),
            ".findc": ("an alias to the '.findcopiedtext' command", self.findCopiedText),
            ".history": ("display history records", self.history),
            ".latestchanges": ("display latest changes", self.latestchanges),
            ".latest": ("display the lastest selection", self.latest),
            ".latestbible": ("display the lastest bible chapter", self.latestBible),
            ".update": ("update Unique Bible App to the latest version", self.update),
            ".commands": ("display available commands", self.commands),
            ".config": ("display UBA configurations", self.config),
            ".showbibles": ("display installed bibles", self.showbibles),
            ".showstrongbibles": ("display installed bibles with Strong's numbers", self.showstrongbibles),
            ".showbiblebooks": ("display bible book list", self.showbiblebooks),
            ".showbibleabbreviations": ("display bible book name list", self.showbibleabbreviations),
            ".showbiblechapters": ("display bible chapter list", self.showbiblechapters),
            ".showbibleverses": ("display bible verse list", self.showbibleverses),
            ".showcommentaries": ("display installed commentaries", self.showcommentaries),
            ".showtopics": ("display installed bible topic modules", self.showtopics),
            ".showlexicons": ("display installed lexicons", self.showlexicons),
            ".showencyclopedia": ("display installed encyclopedia", self.showencyclopedia),
            ".showdictionaries": ("display installed dictionaries", self.showdictionaries),
            ".showthirdpartydictionary": ("display installed third-party dictionaries", self.showthirdpartydictionary),
            ".showreferencebooks": ("display installed reference books", self.showreferencebooks),
            ".showdata": ("display installed data", self.showdata),
            ".showttslanguages": ("display text-to-speech languages", self.showttslanguages),
            ".showdownloads": ("display available downloads", self.showdownloads),
            ".downloadyoutube": ("download youtube file", self.downloadyoutube),
            ".downloadbibleaudio": ("download bible audio", self.downloadbibleaudio),
            ".openbible": ("open bible", self.openbible),
            ".openbiblenote": ("open bible module note", self.openbiblemodulenote),
            ".original": ("open Hebrew & Greek bibles", self.original),
            ".mob": ("open hebrew & Greek original bible", lambda: self.web(".mob", False)),
            ".mib": ("open hebrew & Greek interlinear bible", lambda: self.web(".mib", False)),
            ".mtb": ("open hebrew & Greek trilingual bible", lambda: self.web(".mtb", False)),
            ".mpb": ("open hebrew & Greek parallel bible", lambda: self.web(".mpb", False)),
            ".mab": ("open hebrew & Greek annotated bible", lambda: self.web(".mab", False)),
            ".lxx1i": ("open Septuagint interlinear I", lambda: self.web("TEXT:::LXX1i", False)),
            ".lxx2i": ("open Septuagint interlinear II", lambda: self.web("TEXT:::LXX2i", False)),
            ".open365readingplan": ("open 365-day bible reading plan", self.open365readingplan),
            ".opencommentary": ("open commentary", self.opencommentary),
            ".openreferencebook": ("open reference book", self.openreferencebook),
            ".openaudio": ("open bible audio", self.openbibleaudio),
            ".openbooknote": ("open bible book note", lambda: self.openbookfeature("OPENBOOKNOTE")),
            ".openchapternote": ("open bible chapter note", lambda: self.openchapterfeature("OPENCHAPTERNOTE")),
            ".openversenote": ("open bible verse note", lambda: self.openversefeature("OPENVERSENOTE")),
            ".openjournal": ("open journal", lambda: self.journalFeature("OPENJOURNAL")),
            ".openpromises": ("open bible promises", lambda: self.openTools2("promises")),
            ".openparallels": ("open bible parallels", lambda: self.openTools2("parallels")),
            ".opennames": ("open bible names", lambda: self.openTools2("names")),
            ".opencharacters": ("open bible characters", lambda: self.openTools2("characters")),
            ".openlocations": ("open bible locations", lambda: self.openTools2("locations")),
            ".openmaps": ("open bible maps", self.openmaps),
            ".opendata": ("open bible data", self.opendata),
            ".opentimelines": ("open bible timelines", lambda: self.web(".timelineMenu", False)),
            ".opentopics": ("open bible topics", lambda: self.openTools("TOPICS", self.showtopics)),
            ".opendictionaries": ("open dictionaries", lambda: self.openTools("DICTIONARY", self.showdictionaries)),
            ".openencyclopedia": ("open encyclopedia", lambda: self.openTools("ENCYCLOPEDIA", self.showencyclopedia)),
            ".openlexicons": ("open lexicons", lambda: self.openTools("LEXICON", self.showlexicons)),
            ".openthirdpartydictionaries": ("open third-party dictionaries", lambda: self.openTools("THIRDDICTIONARY", self.showthirdpartydictionary)),
            ".open3dict": ("an alias to the '.openthirdpartydictionaries' command", lambda: self.openTools("THIRDDICTIONARY", self.showthirdpartydictionary)),
            ".editbooknote": ("edit bible book note", lambda: self.openbookfeature("EDITBOOKNOTE")),
            ".editchapternote": ("edit bible chapter note", lambda: self.openchapterfeature("EDITCHAPTERNOTE")),
            ".editversenote": ("edit bible verse note", lambda: self.openversefeature("EDITVERSENOTE")),
            ".editjournal": ("edit journal", lambda: self.journalFeature("EDITJOURNAL")),
            ".quickedit": ("quick edit", lambda: self.quickedit(False)),
            ".qe": ("an alias to the '.quickedit' command", lambda: self.quickedit(False)),
            ".searchbooknote": ("search bible book note", lambda: self.searchNote("SEARCHBOOKNOTE")),
            ".searchchapternote": ("search bible chapter note", lambda: self.searchNote("SEARCHCHAPTERNOTE")),
            ".searchversenote": ("search bible verse note", lambda: self.searchNote("SEARCHVERSENOTE")),
            ".searchjournal": ("search journal", lambda: self.searchNote("SEARCHJOURNAL")),
            ".searchpromises": ("search bible promises", lambda: self.searchTools2("promises")),
            ".searchparallels": ("search bible parallels", lambda: self.searchTools2("parallels")),
            ".searchnames": ("search bible names", lambda: self.searchTools2("names")),
            ".searchcharacters": ("search bible characters", lambda: self.searchTools2("characters")),
            ".searchlocations": ("search bible locations", lambda: self.searchTools2("locations")),
            ".searchdictionaries": ("search dictionaries", lambda: self.searchTools("DICTIONARY", self.showdictionaries)),
            ".searchencyclopedia": ("search encyclopedia", lambda: self.searchTools("ENCYCLOPEDIA", self.showencyclopedia)),
            ".searchlexicons": ("search lexicons", lambda: self.searchTools("LEXICON", self.showlexicons)),
            ".searchlexiconsreversely": ("search lexicons reversely", lambda: self.searchTools("REVERSELEXICON", self.showlexicons)),
            ".searchreferencebooks": ("search reference books", lambda: self.searchTools("BOOK", self.showreferencebooks)),
            ".searchtopics": ("search topics", lambda: self.searchTools("TOPICS", self.showtopics)),
            ".searchthirdpartydictionaries": ("search third-party dictionaries", lambda: self.searchTools("THIRDDICTIONARY", self.showthirdpartydictionary)),
            ".search3dict": ("an alias to the '.searchthirdpartydictionaries' command", lambda: self.searchTools("THIRDDICTIONARY", self.showthirdpartydictionary)),
            ".searchconcordance": ("search for concordance", self.searchconcordance),
            ".quicksearch": ("quick search", lambda: self.quickSearch(False)),
            ".qs": ("an alias to the '.quicksearch' command", lambda: self.quickSearch(False)),
            ".opencrossreference": ("open cross reference", self.openversefeature),
            ".opencomparison": ("open verse comparison", lambda: self.openversefeature("COMPARE")),
            ".opendifference": ("open verse comparison with differences", lambda: self.openversefeature("DIFFERENCE")),
            ".opentske": ("open Treasury of Scripture Knowledge (Enhanced)", lambda: self.openversefeature("TSKE")),
            ".openverseindex": ("open verse index", lambda: self.openversefeature("INDEX")),
            ".opencombo": ("open combination of translation, discourse and words features", lambda: self.openversefeature("COMBO")),
            ".openwords": ("open original words", lambda: self.openversefeature("WORDS")),
            ".opendiscourse": ("open discourse features", lambda: self.openversefeature("DISCOURSE")),
            ".opentranslation": ("open original word translation", lambda: self.openversefeature("TRANSLATION")),
            ".openoverview": ("open chapter overview", self.openchapterfeature),
            ".opensummary": ("open chapter summary", lambda: self.openchapterfeature("SUMMARY")),
            ".openchapterindex": ("open chapter index", lambda: self.openchapterfeature("CHAPTERINDEX")),
            ".openintroduction": ("open book introduction", self.openbookfeature),
            ".opendictionarybookentry": ("open bible book entry in dictionary", lambda: self.openbookfeature("dictionary")),
            ".openencyclopediabookentry": ("open bible book entry in encyclopedia", lambda: self.openbookfeature("encyclopedia")),
            ".openbookfeatures": ("open bible book features", self.openbookfeatures),
            ".openchapterfeatures": ("open bible chapter features", self.openchapterfeatures),
            ".openversefeatures": ("open bible verse features", self.openversefeatures),
            ".quickopen": ("quick open", lambda: self.quickopen(False)),
            ".qo": ("an alias to the '.quickopen' command", lambda: self.quickopen(False)),
            ".standardcommands": ("display standard UBA command help menu", self.standardcommands),
            ".terminalcommands": ("display terminal mode commands", self.terminalcommands),
            ".aliases": ("display terminal mode command shortcuts", self.commandAliases),
            ".menu": ("display main menu", self.menu),
            ".my": ("display my menu", self.my),
            ".show": ("display show menu", self.info),
            ".open": ("display open menu", self.open),
            ".search": ("display search menu", self.search),
            ".note": ("display note / journal menu", self.accessNoteFeatures),
            ".edit": ("display edit menu", self.edit),
            ".quick": ("display quick menu", self.quick),
            ".control": ("display control menu", self.control),
            ".toggle": ("display toggle menu", self.toggle),
            ".clipboard": ("display clipboard menu", self.clipboard),
            ".clip": ("an alias to the '.clipboard' command", self.clipboard),
            ".change": ("display change menu", self.change),
            ".tools": ("display tool menu", self.tools),
            ".plugins": ("display plugin menu", self.plugins),
            ".howto": ("display how-to menu", self.howto),
            ".maintain": ("display maintain menu", self.maintain),
            ".download": ("display download menu", self.download),
            ".backup": ("display backup menu", self.backup),
            ".restore": ("display restore menu", self.restore),
            ".develop": ("display developer menu", self.develop),
            ".help": ("display help menu", self.help),
            ".wiki": ("open online wiki page", self.wiki),
            ".quickstart": ("show how to install text editor micro", lambda: self.readHowTo("quick start")),
            ".helpinstallmicro": ("show how to install text editor micro", lambda: self.readHowTo("install micro")),
            #".w3m": ("open html content in w3m", lambda: self.cliTool("w3m -T text/html", self.html)),
            #".lynx": ("open html content in lynx", lambda: self.cliTool("lynx -stdin", self.html)),
            ".opentext": ("open text from document.", self.opentext),
            ".extract": ("extract bible references from the latest content.", self.extract),
            ".extractcopiedtext": ("extract bible references from the latest content.", self.extractcopiedtext),
            ".editnewfile": ("edit new file in text editor", lambda: self.cliTool(config.terminalNoteEditor)),
            ".editcontent": ("edit latest content in text editor", lambda: self.cliTool(config.terminalNoteEditor, self.getPlainText())),
            ".editconfig": ("edit 'config.py' in text editor", lambda: self.editConfig(config.terminalNoteEditor)),
            ".editfilters": ("edit 'filters.txt' in text editor", self.editfilters),
            ".searchbible": ("search bible", self.searchbible),
            ".whatis": ("read description about a command", self.whatis),
            ".starthttpserver": ("start UBA http-server", self.starthttpserver),
            ".stophttpserver": ("stop UBA http-server", self.stophttpserver),
            ".backupnotes": ("backup note database file", lambda: self.sendFile("marvelData/note.sqlite")),
            ".backupjournals": ("backup journal database file", lambda: self.sendFile("marvelData/journal.sqlite")),
            ".restorenotes": ("restore note database file", lambda: self.restoreFile("marvelData/note.sqlite")),
            ".restorejournals": ("restore journal database file", lambda: self.restoreFile("marvelData/journal.sqlite")),
            ".restorelastnotes": ("restore note database file", lambda: self.restoreLastFile("marvelData/note.sqlite")),
            ".restorelastjournals": ("restore journal database file", lambda: self.restoreLastFile("marvelData/journal.sqlite")),
            ".changemymenu": ("change my menu", self.changemymenu),
            ".changecurrentbible": ("change current bible version", lambda: self.changeDefaultModule("mainText", self.crossPlatform.textList, config.mainText, self.showbibles)),
            ".changefavouritebible1": ("change favourite bible version 1", lambda: self.changeDefaultModule("favouriteBible", self.crossPlatform.textList, config.favouriteBible, self.showbibles)),
            ".changefavouritebible2": ("change favourite bible version 2", lambda: self.changeDefaultModule("favouriteBible2", self.crossPlatform.textList, config.favouriteBible2, self.showbibles)),
            ".changefavouritebible3": ("change favourite bible version 3", lambda: self.changeDefaultModule("favouriteBible3", self.crossPlatform.textList, config.favouriteBible3, self.showbibles)),
            ".changefavouriteoriginalbible": ("change favourite Hebrew & Greek bible", lambda: self.changeDefaultModule("favouriteOriginalBible", self.crossPlatform.textList, config.favouriteOriginalBible, self.showbibles)),
            ".changecommentary": ("change default commentary module", lambda: self.changeDefaultModule("commentaryText", self.crossPlatform.commentaryList, config.commentaryText, self.showcommentaries)),
            ".changelexicon": ("change default lexicon", lambda: self.changeDefaultModule("lexicon", self.crossPlatform.lexiconList, config.lexicon, self.showlexicons)),
            ".changedictionary": ("change default dictionary", lambda: self.changeDefaultModule("dictionary", self.crossPlatform.dictionaryListAbb, config.dictionary, self.showdictionaries)),
            ".changethirdpartydictionary": ("change default third-party dictionary", lambda: self.changeDefaultModule("thirdDictionary", self.crossPlatform.thirdPartyDictionaryList, config.thirdDictionary, self.showthirdpartydictionary)),
            ".changeencyclopedia": ("change default encyclopedia", lambda: self.changeDefaultModule("encyclopedia", self.crossPlatform.encyclopediaListAbb, config.encyclopedia, self.showencyclopedia)),
            ".changeconcordance": ("change default concordance", lambda: self.changeDefaultModule("concordance", self.crossPlatform.strongBibles, config.concordance, self.showstrongbibles)),
            ".changereferencebook": ("change default reference book", lambda: self.changeDefaultModule("book", self.crossPlatform.referenceBookList, config.book, self.showreferencebooks)),
            ".changettslanguage1": ("change default text-to-speech language 1", lambda: self.changeDefaultModule("ttsDefaultLangauge", self.ttsLanguageCodes, config.ttsDefaultLangauge, self.showttslanguages)),
            ".changettslanguage2": ("change default text-to-speech language 2", lambda: self.changeDefaultModule("ttsDefaultLangauge2", self.ttsLanguageCodes, config.ttsDefaultLangauge2, self.showttslanguages)),
            ".changettslanguage3": ("change default text-to-speech language 3", lambda: self.changeDefaultModule("ttsDefaultLangauge3", self.ttsLanguageCodes, config.ttsDefaultLangauge3, self.showttslanguages)),
            ".changedefaultcommand": ("change default command", self.changeDefaultCommand),
            ".changebiblesearchmode": ("change default bible search mode", self.changebiblesearchmode),
            ".changenoteeditor": ("change default note editor", self.changenoteeditor),
            ".changecolors": ("change text highlight colors", self.changecolors),
            ".changecolours": ("an alias to the '.changecolors' command", self.changecolors),
            ".changeconfig": ("change UBA configurations", self.changeconfig),
            ".changeterminalmodeconfig": ("change UBA terminal mode configurations", lambda: self.changeconfig(True)),
            ".gitstatus": ("display git status", self.gitstatus),
            ".exec": ("execute a python string", self.execPythonString),
            ".execfile": ("execute a python file", self.execFile),
            ".reload": ("reload the latest content", self.reload),
            ".restart": ("restart Unique Bible App", self.restartUBA),
            ".z": ("an alias to the '.restart' command", self.restartUBA),
            ".quit": ("quit Unique Bible App", self.quitUBA),
            ".q": ("an alias to the '.quit' command", self.quitUBA),
            ".googletranslate": ("translate with Google Translate", lambda: self.googleTranslate(False)),
            ".googletranslatecopiedtext": ("translate copied text with Google Translate", self.googleTranslate),
            ".gt": ("an alias to the '.googletranslate' command", lambda: self.googleTranslate(False)),
            ".gtc": ("an alias to the '.googletranslatecopiedtext' command", self.googleTranslate),
            ".watsontranslate": ("translate with IBM Watson Translator", lambda: self.watsonTranslate(False)),
            ".watsontranslatecopiedtext": ("translate copied text with IBM Watson Translator", self.watsonTranslate),
            ".wt": ("an alias to the '.watsontranslate' command", lambda: self.watsonTranslate(False)),
            ".wtc": ("an alias to the '.watsontranslatecopiedtext' command", self.watsonTranslate),
            ".buildportablepython": ("build portable python", self.buildPortablePython),
        }

    def editfilters(self):
        savedFiltersFile = os.path.join("terminal_mode", "filters.txt")
        print(f"You are about to edit '{savedFiltersFile}' ...")
        print("Save as and overwrite the file '{savedFiltersFile}' when you finish.")
        print("Are you ready to edit? [y]es / [N]o")
        userInput = self.simplePrompt()
        if userInput.lower() in ("y", "yes"):
            text = self.readPlainTextFile(savedFiltersFile)
            return self.cliTool(config.terminalNoteEditor, text)
        else:
            self.cancelAction()

    def filters(self):
        try:
            savedFiltersFile = os.path.join("terminal_mode", "filters.txt")
            if not os.path.isfile(savedFiltersFile):
                with open(savedFiltersFile, "w", encoding="utf-8") as fileObj:
                    fileObj.write("jesus|christ\nGen \nJohn ")
            with open(savedFiltersFile, "r", encoding="utf-8") as input_file:
                savedFiltersFileContent = input_file.read()
            savedFilters = [i for i in savedFiltersFileContent.split("\n") if i.strip()]
            print(self.divider)
            print(TextUtil.htmlToPlainText("<h2>Saved Filters are:</h2>"))
            print(pprint.pformat(savedFilters))
            print(self.divider)
            print("Enter mulitple filters:")
            print("(enter each on a single line)")
            print("(newly added filters will be automatically saved)")
            if config.isPrompt_toolkitInstalled:
                self.printMultineNote()
                userInput = self.terminal_live_filter_session.prompt(self.inputIndicator, style=self.promptStyle, multiline=True).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            currentFilters = []
            for i in userInput.split("\n"):
                if i.strip():
                    if not i in savedFilters:
                        savedFilters.append(i)
                    currentFilters.append(i)
            if not currentFilters:
                return self.reload()
            filteredText = []
            for line in self.plainText.split("\n"):
                match = True
                for f in currentFilters:
                    # check if any one of the filters is not matched
                    if not TextUtil.regexp(f, line):
                        match = False
                        break
                # display when a line matches all filters
                if match:
                    filteredText.append(line)
            # update saved filters
            with open(savedFiltersFile, "w", encoding="utf-8") as fileObj:
                fileObj.write("\n".join(sorted(savedFilters)))
            # display filtered text
            return self.displayOutputOnTerminal("\n".join(filteredText))
        except:
            print("Errors!")
        return ""

    def execPythonString(self):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
        try:
            print(self.divider)
            print("Enter a python script:")
            if config.isPrompt_toolkitInstalled:
                self.printMultineNote()
                userInput = self.terminal_python_string_session.prompt(self.inputIndicator, style=self.promptStyle, multiline=True).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            exec(userInput, globals())
        except:
            print("Errors!")
        return ""

    def execFile(self):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
        try:
            print(self.divider)
            print("Enter a python file path:")
            if config.isPrompt_toolkitInstalled:
                userInput = self.terminal_python_file_session.prompt(self.inputIndicator, style=self.promptStyle).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            self.execPythonFile(userInput)
        except:
            print("Errors!")
        return ""

    def plugins(self):
        availablePlugins = FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "terminal"), "py")
        print(self.divider)
        self.printOptionsDisplay(availablePlugins, "Plugins")
        print(self.divider)
        print("Enter a number:")
        userInput = self.simplePrompt(True)
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        #try:
        filepath = os.path.join("plugins", "terminal", f"{availablePlugins[int(userInput)]}.py")
        self.execPythonFile(filepath)
        return ""
        #except:
        #    return self.printInvalidOptionEntered()

    def howto(self):
        availableHowto = FileUtil.fileNamesWithoutExtension(os.path.join("terminal_mode", "how_to"), "md")
        print(self.divider)
        self.printOptionsDisplay(availableHowto, "Plugins")
        print(self.divider)
        print("Enter a number:")
        userInput = self.simplePrompt(True)
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        try:
            filepath = os.path.join("terminal_mode", "how_to", f"{availableHowto[int(userInput)]}.md")
            return self.readPlainTextFile(filepath)
        except:
            return self.printInvalidOptionEntered()

    def execPythonFile(self, script):
        self.crossPlatform.execPythonFile(script)

    # a dummy method to work with config.mainWindow.runTextCommand in some codes
    def runTextCommand(self, command):
        return self.getContent(command)

    def getContent(self, command, checkDotCommand=True):
        command = command.strip()
        # allow use of tts::: no matter which tts engine is in place
        if command.lower().startswith("tts:::"):
            command = f"{self.ttsCommandKeyword}{command[3:]}"
        # study window applies to Qt library users only
        if command.lower().startswith("study:::") or command.lower().startswith("studytext:::"):
            config.studyText, config.studyB, config.studyC, config.studyV = config.mainText, config.mainB, config.mainC, config.mainV
        originalCommand = command
        # Shortcuts to change chapter or verse or both chapter and verse for bible reading.
        if command:
            try:
                bc = command.split(":", 1)
                bci = [int(i) for i in bc if i]
                if len(bc) == 2 and len(bci) == 1:
                    # Users specify a verse number, e.g. :16
                    if command.startswith(":"):
                        command = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, bci[0])
                    # Users specify a chapter number, e.g. 3:
                    elif command.endswith(":"):
                        command = self.textCommandParser.bcvToVerseReference(config.mainB, bci[0], 1)
                # Users specify both a chapter number and a verse number, e.g. 3:16
                elif len(bc) == 2 and len(bci) == 2:
                    command = self.textCommandParser.bcvToVerseReference(config.mainB, bci[0], bci[1])
                if not originalCommand == command:
                    prefix = f"COMPARE:::{config.compareParallelList}:::" if config.terminalBibleComparison else "BIBLE:::"
                    command = f"{prefix}{command}"
                    self.printRunningCommand(command)
            except:
                pass
        # Redirect heavy html content to web version.
        if not command.lower().startswith(".") and re.search('^(map:::|qrcode:::|bible:::mab:::|bible:::mib:::|bible:::mob:::|bible:::mpb:::|bible:::mtb:::|text:::mab|text:::mib|text:::mob|text:::mpb|text:::mtb|study:::mab:::|study:::mib:::|study:::mob:::|study:::mpb:::|study:::mtb:::|studytext:::mab|studytext:::mib|studytext:::mob|studytext:::mpb|studytext:::mtb)', command.lower()):
            return self.web(command)
        # Dot commands
        if checkDotCommand and command.startswith("."):
            return self.getDotCommandContent(command.lower())
        # Non-dot commands
        view, content, dict = self.textCommandParser.parser(command, "cli")
        # keep record of last command
        self.command = command
        if config.bibleWindowContentTransformers:
            for transformer in config.bibleWindowContentTransformers:
                content = transformer(content)
        if content:
            #self.crossPlatform.addHistoryRecord(view, command)
            self.html = content
        else:
            content = "Command processed!"
        # Convert html to plain text
        plainText = TextUtil.htmlToPlainText(content).strip()
        self.plainText = "" if content == "Command processed!" else plainText
        # Update main text, b, c, v
        references = self.textCommandParser.extractAllVerses(command)
        if references:
            config.mainB, config.mainC, config.mainV, *_ = references[-1]
        return plainText

    def fineTuneTextForWebBrowserDisplay(self, text=""):
        if not text:
            text = self.html
        if text.startswith("[BROWSER]"):
            text = text[9:]
        text = re.sub("audiotrack", "", text)
        text = re.sub("「(Back|Fore|Style)\.[^「」]+?」", "", text)
        return text

    def displayOutputOnTerminal(self, content):
        if content.startswith("[BROWSER]"):
            html = self.fineTuneTextForWebBrowserDisplay()
            self.cliTool("w3m -T text/html", html)
        else:
            divider = self.divider
            if config.terminalEnablePager and not content in ("Command processed!", "INVALID_COMMAND_ENTERED") and not content.endswith("not supported in terminal mode.") and not content.startswith("[MESSAGE]"):
                if platform.system() == "Windows":
                    try:
                        pydoc.pager(content)
                    except:
                        config.terminalEnablePager = False
                        print(divider)
                        print(content)
                    # When you use remote powershell and want to pipe a command on the remote windows server through a pager, piping through out-host -paging works as desired. Piping through more when running the remote command is of no use: the entire text is displayed at once.
    #                try:
    #                    pydoc.pipepager(content, cmd='out-host -paging')
    #                except:
    #                    try:
    #                        pydoc.pipepager(content, cmd='more')
    #                    except:
    #                        config.terminalEnablePager = False
    #                        print(divider)
    #                        print(content)
                else:
                    try:
                        # paging without colours
                        #pydoc.pager(content)
                        # paging with colours
                        pydoc.pipepager(content, cmd='less -R')
                    except:
                        config.terminalEnablePager = False
                        print(divider)
                        print(content)
            else:
                if content.startswith("[MESSAGE]"):
                    content = content[9:]
                print(divider)
                print(content)
        self.checkAudioContent()

    def quitUBA(self):
        print("Closing ...")
        return ""

    def restartUBA(self):
        print("Restarting ...")
        return ""

    def getDotCommandContent(self, command):
        enteredCommand = command
        command = command.replace(" ", "")
        if command in self.dotCommands:
            return self.dotCommands[command][-1]()
        return self.getContent(enteredCommand, False)
        #print(f"Command not found: {command}")
        #return ""

    def getDummyDict(self, data, suffix="", furtherOptions=None):
        # set is supported in NestedCompleter but not preferred as set is unordered
        return {f"{i}{suffix}": furtherOptions for i in data} if furtherOptions is not None else {f"{i}{suffix}": None for i in data}

    def getCommandCompleter(self):
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit.completion import NestedCompleter, ThreadedCompleter

            suggestions = {}
            days365 = self.getDummyDict([(i + 1) for i in range(365)])
            for i in self.getTextCommandSuggestion():
                if re.sub(":::$", "", i) in self.unsupportedCommands:
                    pass
                elif i == ".backup":
                    suggestions[i] = self.getDummyDict(["journals", "notes",])
                elif i == ".copy":
                    suggestions[i] = self.getDummyDict(["html",])
                elif i == ".download":
                    suggestions[i] = self.getDummyDict(["bibleaudio", "youtube",])
                elif i == ".extract":
                    suggestions[i] = self.getDummyDict(["copiedtext",])
                elif i == ".find":
                    suggestions[i] = self.getDummyDict(["copiedtext",])
                elif i == ".help":
                    suggestions[i] = self.getDummyDict(["installmicro",])
                elif i == ".latest":
                    suggestions[i] = self.getDummyDict(["bible", "changes",])
                elif i == ".read":
                    suggestions[i] = self.getDummyDict(["sync",])
                elif i == ".restore":
                    suggestions[i] = self.getDummyDict(["journals", "lastjournals", "lastnotes", "notes",])
                elif i == ".tts":
                    suggestions[i] = self.getDummyDict(["copiedtext",])
                elif i == ".change":
                    suggestions[i] = self.getDummyDict(["biblesearchmode", "colors", "colours", "commentary", "concordance", "config", "currentbible", "defaultcommand", "dictionary", "encyclopedia", "favouritebible1", "favouritebible2", "favouritebible3", "favouriteoriginalbible", "lexicon", "mymenu", "noteeditor", "referencebook", "terminalmodeconfig", "thirdpartydictionary", "ttslanguage1", "ttslanguage2", "ttslanguage3"])
                elif i == ".exec":
                    suggestions[i] = self.getDummyDict(["file",])
                elif i == ".edit":
                    suggestions[i] = self.getDummyDict(["booknote", "chapternote", "config", "content", "filters", "journal", "newfile", "versenote"])
                elif i == ".open":
                    suggestions[i] = self.getDummyDict(["365readingplan", "3dict", "audio", "bible", "biblenote", "bookfeatures", "booknote", "chapterfeatures", "chapterindex", "chapternote", "characters", "combo", "commentary", "comparison", "crossreference", "data", "dictionaries", "dictionarybookentry", "difference", "discourse", "encyclopedia", "encyclopediabookentry", "introduction", "journal", "lexicons", "locations", "maps", "names", "overview", "parallels", "promises", "referencebook", "summary", "text", "thirdpartydictionaries", "timelines", "topics", "translation", "tske", "versefeatures", "verseindex", "versenote", "words"])
                elif i == ".quick":
                    suggestions[i] = self.getDummyDict(["edit", "editcopiedtext", "open", "opencopiedtext", "search", "searchcopiedtext", "start"])
                elif i == ".search":
                    suggestions[i] = self.getDummyDict(["3dict", "bible", "booknote", "chapternote", "characters", "concordance", "dictionaries", "encyclopedia", "journal", "lexicons", "lexiconsreversely", "locations", "names", "parallels", "promises", "referencebooks", "thirdpartydictionaries", "topics", "versenote"])
                elif i == ".show":
                    suggestions[i] = self.getDummyDict(["bibleabbreviations", "biblebooks", "biblechapters", "bibles", "bibleverses", "commentaries", "data", "dictionaries", "downloads", "encyclopedia", "lexicons", "referencebooks", "strongbibles", "thirdpartydictionary", "topics", "ttslanguages"])
                elif i == ".toggle":
                    suggestions[i] = self.getDummyDict(["biblechapterplainlayout", "biblecomparison", "biblelexicalentries", "biblenoteindicator", "clipboardmonitor", "favoriteverses", "favouriteverses", "pager", "plainbiblechaptersubheadings", "usernoteindicator", "versenumberdisplay"])
                elif i in ("text:::", "studytext:::", "_chapters", "_bibleinfo:::"):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.textList)
                elif i in ("_vnsc:::", "_vndc:::", "readchapter:::", "readverse:::", "readword:::", "readlexeme:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.textList, ".")
                elif i in ("compare:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.textList, "_")
                elif i in ("search:::", "searchall:::", "andsearch:::", "orsearch:::", "advancedsearch:::", "regexsearch:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.textList, ":::")
                elif i in ("bible:::", "main:::", "study:::", "read:::", "readsync:::", "_verses:::"):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.textList, ":::", None if config.terminalUseLighterCompleter else self.allKJVreferences)
                elif i in ("_biblenote:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.textList, ":::", None if config.terminalUseLighterCompleter else self.allKJVreferencesBcv1)
                elif i in ("concordance:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.strongBibles, ":::")
                elif i in ("lexicon:::", "searchlexicon:::", "reverselexicon",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.lexiconList, ":::")
                elif i in ("data:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.dataList)
                elif i in ("translate:::",):
                    suggestions[i] = self.getDummyDict(Translator.fromLanguageCodes, "-")
                elif i in ("download:::",):
                    downloadTypes = ["MarvelData", "MarvelBible", "MarvelCommentary", "GitHubBible", "GitHubCommentary", "GitHubBook", "GitHubMap", "GitHubPdf", "GitHubEpub"]
                    suggestions[i] = self.getDummyDict(downloadTypes, ":::")
                elif i in ("_commentarychapters:::", "_commentaryinfo:::"):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.commentaryList)
                elif i in ("commentary:::", "_commentaryverses:::"):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.commentaryList, ":::", None if config.terminalUseLighterCompleter else self.allKJVreferences)
                elif i in ("commentary2:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.commentaryList, ":::", None if config.terminalUseLighterCompleter else self.allKJVreferencesBcv1)
                elif i in ("_commentary:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.commentaryList, ".")
                elif i in ("crossreference:::", "difference:::", "diff:::", "passages:::", "overview:::", "summary:::", "index:::", "chapterindex:::", "map:::", "tske:::", "combo:::", "translation:::", "discourse:::", "words:::", "openbooknote:::", "openchapternote:::", "openversenote:::", "editbooknote:::", "editchapternote:::", "editversenote:::", "_imvr:::"):
                    suggestions[i] = self.allKJVreferences
                elif i in ("_imv:::", "_instantverse:::", "_menu:::", "_openbooknote:::", "_openchapternote:::", "_openversenote:::", "_editbooknote:::", "_editchapternote:::", "_editversenote:::"):
                    suggestions[i] = self.allKJVreferencesBcv1
                elif i in ("clause:::",):
                    suggestions[i] = self.allKJVreferencesBcv2
                elif i in ("dictionary:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.dictionaryListAbb, ":::")
                elif i in ("encyclopedia:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.encyclopediaListAbb, ":::")
                elif i in ("_book:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.referenceBookList)
                elif i in ("book:::", "searchbook:::", "searchbookchapter:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.referenceBookList, ":::")
                elif i in ("thirddictionary:::", "searchthirddictionary:::", "s3dict:::", "3dict:::"):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.thirdPartyDictionaryList, ":::")
                elif i in ("searchtool:::",):
                    suggestions[i] = self.getDummyDict(self.crossPlatform.searchToolList, ":::")
                elif i in (f"{self.ttsCommandKeyword}:::",):
                    suggestions[i] = self.getDummyDict(self.ttsLanguageCodes, ":::")
                elif i in ("exlb:::",):
                    suggestions[i] = self.getDummyDict(["exlbt", "exlbp", "exlbl"], ":::")
                elif i in ("day:::", "dayaudio:::", "dayaudioplus:::"):
                    suggestions[i] = days365
                elif i in ("_whatis:::",):
                    options = sorted(list(self.dotCommands.keys())) + list(self.textCommandParser.interpreters.keys())
                    suggestions[i] = self.getDummyDict(options)
                else:
                    suggestions[i] = None
            # Added all KJV verse references
            suggestions = {**suggestions, **self.allKJVreferences}
            # Remove unexpected item
            suggestions.pop(":::", None)
            if config.terminalUseLighterCompleter:
                completer = ThreadedCompleter(NestedCompleter.from_nested_dict(suggestions))
            else:
                completer = ThreadedCompleter(NestedCompleter.from_nested_dict(suggestions))
            return completer

    def getTextCommandSuggestion(self, addDotCommandWordOnly=True):
        # Text command autocompletion/autosuggest
        textCommands = [key + ":::" for key in self.textCommandParser.interpreters.keys()]
        bibleBooks = self.bibleBooks.getStandardBookAbbreviations()
        dotCommands = sorted(list(self.dotCommands.keys()))
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        if addDotCommandWordOnly:
            #suggestion = ['.quit', '.restart', 'quit', 'restart', bibleReference] + dotCommands + [cmd[1:] for cmd in dotCommands] + sorted(textCommands) + bibleBooks
            #suggestion = ['.quit', '.restart', 'quit', 'restart', bibleReference] + dotCommands + [cmd[1:] for cmd in dotCommands] + sorted(textCommands)
            suggestion = [bibleReference] + dotCommands + sorted(textCommands)
        else:
            suggestion = dotCommands + sorted(textCommands) + bibleBooks
            suggestion.sort()
        return suggestion

    def togglePager(self):
        config.terminalEnablePager = not config.terminalEnablePager
        return self.plainText

    def showClipboardMonitorStatus(self):
        print(self.divider)
        print("Clipboard Monitor:", "ON" if config.terminalEnableClipboardMonitor else "OFF")

    def toggleClipboardMonitor(self):
        config.terminalEnableClipboardMonitor = not config.terminalEnableClipboardMonitor
        self.showClipboardMonitorStatus()
        return ""

    def standardcommands(self):
        content = "UBA commands:"
        #content += "\n".join([f"{key} - {self.dotCommands[key][0]}" for key in sorted(self.dotCommands.keys())])
        content += "\n".join([re.sub("            #", "#", value[-1]) for value in self.textCommandParser.interpreters.values()])
        return self.keepContent(content)

    def terminalcommands(self):
        content = "UBA terminal mode commands:"
        content += "\n".join([f"{key} - {self.dotCommands[key][0]}" for key in sorted(self.dotCommands.keys())])
        print(self.keepContent(content))
        return ""

    def commandAliases(self):
        content = "UBA terminal mode command aliases:"
        content += "\n".join([f"{key} - {value[0]}" for key, value in sorted(self.dotCommands.items()) if value[0].startswith("an alias to ")])
        print(self.keepContent(content))
        return ""

    def open365readingplan(self):
        days = "<br>".join([f"[<ref>{i}</ref> ] <ref>{text[-1]}</ref>" for i, text in allDays.items()])
        days = f"<h2>365 Day Reading Plan</h2>{days}"
        print(self.divider)
        print(TextUtil.htmlToPlainText(days).strip())
        print(self.divider)
        print("Enter a day number")
        userInput = self.simplePrompt(True)
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        try:
            if int(userInput) and int(userInput) in range(366):
                command = f"DAY:::{userInput}"
                self.printRunningCommand(command)
                return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def stopAudio(self):
        self.textCommandParser.parent.closeMediaPlayer()
        return ""

    def reload(self):
        return self.plainText

    def keepContent(self, content):
        self.html = re.sub("\n", "<br>", content)
        self.plainText = content
        return content

    def commands(self):
        content = pprint.pformat(self.getTextCommandSuggestion(False))
        return self.keepContent(content)

    def read(self):
        self.textCommandParser.parent.getPlaylistFromHTML(self.html)
        return ""

    def readsync(self):
        self.textCommandParser.parent.getPlaylistFromHTML(self.html, displayText=True)
        return ""

    def latest(self):
        print(self.divider)
        server = "http://localhost:8080"
        serverAlive = "ON" if self.isUrlAlive(server) else "OFF"
        print(f"{server} [{serverAlive}]")
        searchModes = ("SEARCH", "SEARCHALL", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
        print(f"Current search mode: {searchModes[config.bibleSearchMode]}")
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        print("BIBLE:::{0}:::{1} [{2}.{3}.{4}]".format(config.mainText, bibleReference, config.mainB, config.mainC, config.mainV))
        commentaryReference = self.textCommandParser.bcvToVerseReference(config.commentaryB, config.commentaryC, config.commentaryV)
        print("COMMENTARY:::{0}:::{1} [{2}.{3}.{4}]".format(config.commentaryText, commentaryReference, config.commentaryB, config.commentaryC, config.commentaryV))
        print(f"BOOK:::{config.book}:::{config.bookChapter}")
        print(f"LEXICON:::{config.lexicon}:::{config.lexiconEntry}")
        print(f"CONCORDANCE:::{config.concordance}:::{config.concordanceEntry}")
        print(f"DICTIONARY:::{config.dictionaryEntry}")
        print(f"ENCYCLOPEDIA:::{config.encyclopedia}:::{config.encyclopediaEntry}")
        print(f"THIRDDICTIONARY:::{config.thirdDictionary}:::{config.thirdDictionaryEntry}")
        print(f"DATA:::{config.dataset}")
        print(f"EXLB:::exlbt:::{config.topicEntry}")
        print(f"EXLB:::exlbp:::{config.characterEntry}")
        print(f"EXLB:::exlbl:::{config.locationEntry}")
        print(f"_harmony:::{config.parallels}.{config.parallelsEntry}")
        print(f"_promise:::{config.promises}.{config.promisesEntry}")
        return ""

    def getPlusBible(self):
        plusBible = ""
        if not config.mainText == config.favouriteBible:
            plusBible = config.favouriteBible
        elif not config.mainText == config.favouriteBible2:
            plusBible = config.favouriteBible2
        elif not config.mainText == config.favouriteBible3:
            plusBible = config.favouriteBible3
        if plusBible:
            return f", {plusBible}"
        return plusBible

    def checkAudioContent(self):
        if config.audioBibleIcon in self.html or config.audioBibleIcon2 in self.html:
            print(self.divider)
            print("Audio content is available!")
            print("To listen, run '.read' or '.readsync'")

    def initialDisplay(self):
        print(self.divider)
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        print("{0} [{1}.{2}.{3}] - {4}{5}, {6}".format(bibleReference, config.mainB, config.mainC, config.mainV, config.mainText, self.getPlusBible(), config.commentaryText))
        print("Enter an UBA command:")
        if config.terminalDisplayBeginnerMessage:
            print("(run '.menu' to begin ...)")
        return ""

    def showbibleabbreviations(self, text="", commentary=False):
        bible = Bible(config.mainText if not text else text)
        bibleBooks = self.bibleBooks
        bookNumbers = bible.getBookList()
        print([f"[{b}] {bibleBooks.getStandardBookAbbreviation(b)}" for b in bookNumbers])
        self.currentBibleAbbs = [bibleBooks.getStandardBookAbbreviation(b) for b in bookNumbers]
        try:
            if commentary:
                self.currentBibleAbb = bibleBooks.getStandardBookAbbreviation(config.commentaryB)
            else:
                self.currentBibleAbb = bibleBooks.getStandardBookAbbreviation(config.mainB)
        except:
            self.currentBibleAbb = self.currentBibleAbbs[0]
        self.bookNumbers = bookNumbers
        return ""

    def showbiblebooks(self, text=""):
        bible = Bible(config.mainText if not text else text)
        bibleBooks = self.bibleBooks
        bookNumbers = bible.getBookList()
        print([f"[{b}] {bibleBooks.getStandardBookFullName(b)}" for b in bookNumbers])
        self.currentBibleBooks = [bibleBooks.getStandardBookFullName(b) for b in bookNumbers]
        try:
            self.currentBibleBook = bibleBooks.getStandardBookFullName(config.mainB)
        except:
            self.currentBibleBook = self.currentBibleBooks[0]
        self.bookNumbers = bookNumbers
        return ""

    def wiki(self):
        url = "https://github.com/eliranwong/UniqueBible/wiki/Terminal-Mode"
        command = f"_website:::{url}"
        self.printRunningCommand(command)
        return self.getContent(command)

    def showbiblechapters(self, text="", b=None):
        bible = Bible(config.mainText if not text else text)
        chapterList = bible.getChapterList(config.mainB if b is None else b)
        print(chapterList)
        self.currentBibleChapters = chapterList
        return ""

    def showbibleverses(self, text="", b=None, c=None):
        bible = Bible(config.mainText if not text else text)
        verseList = bible.getVerseList(config.mainB if b is None else b, config.mainC if c is None else c)
        print(verseList)
        self.currentBibleVerses = verseList
        return ""

    def showtopics(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_topics"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.topicListAbb):
            moduleList.append(f"[<ref>{topic}</ref> ] {self.crossPlatform.topicList[index]}")
        content += "<br>".join(moduleList)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showdictionaries(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["context1_dict"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.dictionaryListAbb):
            moduleList.append(f"[<ref>{topic}</ref> ] {self.crossPlatform.dictionaryList[index]}")
        content += "<br>".join(moduleList)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showencyclopedia(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["context1_encyclopedia"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.encyclopediaListAbb):
            moduleList.append(f"[<ref>{topic}</ref> ] {self.crossPlatform.encyclopediaList[index]}")
        content += "<br>".join(moduleList)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showbibles(self):
        #return pprint.pformat(dict(zip(self.crossPlatform.textList, self.crossPlatform.textFullNameList)))
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_bible"])
        bibleList = []
        for index, bible in enumerate(self.crossPlatform.textList):
            bibleList.append(f"[<ref>{bible}</ref> ] {self.crossPlatform.textFullNameList[index]}")
        content += "<br>".join(bibleList)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showstrongbibles(self):
        strongBiblesFullNameList = [Bible(text).bibleInfo() for text in self.crossPlatform.strongBibles]
        content = ""
        content += "<h2>{0} + {1}</h2>".format(config.thisTranslation["menu5_bible"], config.thisTranslation["bibleStrongNumber"])
        bibleList = []
        for index, bible in enumerate(self.crossPlatform.strongBibles):
            bibleList.append(f"[<ref>{bible}</ref> ] {strongBiblesFullNameList[index]}")
        content += "<br>".join(bibleList)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showthirdpartydictionary(self):
        modules = []
        for module in self.crossPlatform.thirdPartyDictionaryList:
            modules.append(f"[<ref>{module}</ref> ]")
        content = "<br>".join(modules)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showlexicons(self):
        modules = []
        for module in self.crossPlatform.lexiconList:
            modules.append(f"[<ref>{module}</ref> ]")
        content = "<br>".join(modules)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showcommentaries(self):
        #self.crossPlatform.setupResourceLists()
        content = ""
        content += """<h2><ref onclick="window.parent.submitCommand('.commentarymenu')">{0}</ref></h2>""".format(config.thisTranslation["menu4_commentary"])
        content += "<br>".join(["""[<ref>{0}</ref> ] {1}""".format(abb, self.crossPlatform.commentaryFullNameList[index]) for index, abb in enumerate(self.crossPlatform.commentaryList)])
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showreferencebooks(self):
        #self.crossPlatform.setupResourceLists()
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_selectBook"])
        content += "<br>".join(["""[<ref>{0}</ref> ] {0}""".format(book) for book in self.crossPlatform.referenceBookList])
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showdata(self):
        #self.crossPlatform.setupResourceLists()
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu_data"])
        content += "<br>".join(["[<ref>{0}</ref> ]".format(book) for book in self.crossPlatform.dataList])
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showdownloads(self):
        content = ""
        from util.DatafileLocation import DatafileLocation
        from util.GithubUtil import GithubUtil
        # ["marveldata", "marvelbible", "marvelcommentary", "GitHubBible", "GitHubCommentary", "GitHubBook", "GitHubMap", "GitHubPdf", "GitHubEpub"]
        resources = (
            ("Marvel Datasets", DatafileLocation.marvelData, "marveldata"),
            ("Marvel Bibles", DatafileLocation.marvelBibles, "marvelbible"),
            ("Marvel Commentaries", DatafileLocation.marvelCommentaries, "marvelcommentary"),
        )
        for collection, data, keyword in resources:
            content += "<h2>{0}</h2>".format(collection)
            for k, v in data.items():
                if os.path.isfile(os.path.join(*v[0])):
                    content += """[ {1} ] {0}<br>""".format(k, config.thisTranslation["installed"])
                else:
                    content += """[<ref>DOWNLOAD:::{0}:::{1}</ref> ]<br>""".format(keyword, k)
        resources = (
            ("GitHub Bibles", "GitHubBible", GitHubRepoInfo.bibles[0], (config.marvelData, "bibles"), ".bible"),
            ("GitHub Commentaries", "GitHubCommentary", GitHubRepoInfo.commentaries[0], (config.marvelData, "commentaries"), ".commentary"),
            ("GitHub Books", "GitHubBook", GitHubRepoInfo.books[0], (config.marvelData, "books"), ".book"),
            ("GitHub Maps", "GitHubMap", GitHubRepoInfo.maps[0], (config.marvelData, "books"), ".book"),
            ("GitHub PDF", "GitHubPdf", GitHubRepoInfo.pdf[0], (config.marvelData, "pdf"), ".pdf"),
            ("GitHub EPUB", "GitHubEpub", GitHubRepoInfo.epub[0], (config.marvelData, "epub"), ".epub"),
        )
        for collection, type, repo, location, extension in resources:
            content += "<h2>{0}</h2>".format(collection)
            for file in GithubUtil(repo).getRepoData():
                if os.path.isfile(os.path.join(*location, file)):
                    content += """[ {1} ] {0}<br>""".format(file.replace(extension, ""), config.thisTranslation["installed"])
                else:
                    content += """[<ref>DOWNLOAD:::{1}:::{0}</ref> ]<br>""".format(file.replace(extension, ""), type)
        content += "<h2>Third-party Resources</h2><p>Read <ref>https://github.com/eliranwong/UniqueBible/wiki/Third-party-resources</ref> about third-party resources.</a></p>"
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def getCliOutput(self, cli):
        try:
            process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = process.communicate()
            return stdout.decode("utf-8")
        except:
            return ""

    def gitstatus(self):
        return self.getCliOutput("git status")

    def showttslanguages(self):
        codes = self.ttsLanguageCodes

        display = "<h2>Languages</h2>"
        languages = []
        for code in codes:
            language = self.ttsLanguages[code][-1]
            languages.append(language)
            display += f"[<ref>{code}</ref> ] {language}<br>"
        display = display[:-4]
        self.html = display
        self.plainText = TextUtil.htmlToPlainText(display).strip()
        print(self.plainText)
        return ""

    def getDefaultTtsKeyword(self):
        if config.isGoogleCloudTTSAvailable:
            return "GTTS"
        elif (not config.isOfflineTtsInstalled or config.forceOnlineTts) and config.isGTTSInstalled:
            return "GTTS"
        elif config.macVoices:
            return "SPEAK"
        elif config.espeak:
            return "SPEAK"
        else:
            return "SPEAK"

    def extract(self, text=""):
        if not text:
            text = self.plainText
        parser = BibleVerseParser(config.parserStandarisation)
        verseList = parser.extractAllReferences(text, False)
        #print(self.divider)
        if not verseList:
            print("No bible reference is found!")
        else:
            print("Bible reference(s):")
            references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])
            print(references)
        return ""

    def extractcopiedtext(self):
        clipboardText = self.getclipboardtext()
        self.html = clipboardText
        self.plainText = clipboardText
        return self.extract()

    def findCopiedText(self):
        clipboardText = self.getclipboardtext()
        self.html = clipboardText
        self.plainText = clipboardText
        return self.find()

    def changeDefaultModule(self, configitem, options, default="", displayMethod=None):
        print(self.divider)
        if displayMethod is not None:
            display = displayMethod()
            if display:
                print(display)
        print(self.divider)
        print("Enter an abbreviation")
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            from prompt_toolkit.completion import WordCompleter
            completer = WordCompleter(options, ignore_case=True)
            userInput = prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=default).strip()
        else:
            userInput = input(self.inputIndicator).strip()
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        if userInput in options:
            command = f"_setconfig:::{configitem}:::'{userInput}'"
            self.printRunningCommand(command)
            return self.getContent(command)
        else:
            return self.printInvalidOptionEntered()

    def tts(self, runOnCopiedText=True):
        if runOnCopiedText:
            clipboardText = self.getclipboardtext()
        codes = self.ttsLanguageCodes
        #display = "<h2>Languages</h2>"
        shortCodes = []
        languages = []
        for code in codes:
            shortCodes.append(re.sub("\-.*?$", "", code))
            languages.append(self.ttsLanguages[code])
            #display += f"[<ref>{codes}</ref> ] {languages}<br>"
        #display = display[:-4]

        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showttslanguages())
            self.printChooseItem()
            print("Enter a language code:")
            if config.isPrompt_toolkitInstalled:
                suggestions = shortCodes + codes
                suggestions = list(set(suggestions))
                completer = WordCompleter(suggestions, ignore_case=True)
                default = config.ttsDefaultLangauge if config.ttsDefaultLangauge in suggestions else ""
                userInput = self.terminal_tts_language_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=default).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in suggestions:
                config.ttsDefaultLangauge = userInput
                commandPrefix = f"{self.getDefaultTtsKeyword()}:::{userInput}:::"
                if runOnCopiedText:
                    userInput = clipboardText
                else:
                    print(self.divider)
                    print("Enter text to be read:")
                    userInput = self.simplePrompt(multiline=True)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()

                command = f"{commandPrefix}{userInput}"
                self.printRunningCommand(command)
                return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def watsonTranslate(self, runOnCopiedText=True):
        if config.isIbmWatsonInstalled:
            if runOnCopiedText:
                clipboardText = self.getclipboardtext()
            try:
                if config.isPrompt_toolkitInstalled:
                    from prompt_toolkit.completion import WordCompleter

                codes = []
                display = []
                for index, item in enumerate(Translator.fromLanguageCodes):
                    display.append(f"[<ref>{item}</ref> ] {Translator.fromLanguageNames[index]}")
                    codes.append(item)
                display = "<br>".join(display)
                display = TextUtil.htmlToPlainText(f"<h2>Languages</h2>{display}")

                print(self.divider)
                print(display)
                print("Translate from:")
                print("(enter a language code)")
                if config.isPrompt_toolkitInstalled:
                    suggestions = codes
                    completer = WordCompleter(suggestions, ignore_case=True)
                    userInput = self.terminal_watson_translate_from_language_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in suggestions:
                    fromLanguage = userInput

                    codes = []
                    display = []
                    for index, item in enumerate(Translator.toLanguageCodes):
                        display.append(f"[<ref>{item}</ref> ] {Translator.toLanguageNames[index]}")
                        codes.append(item)
                    display = "<br>".join(display)
                    display = TextUtil.htmlToPlainText(f"<h2>Languages</h2>{display}")

                    print(self.divider)
                    print(display)
                    print("Translate to:")
                    print("(enter a language code)")
                    if config.isPrompt_toolkitInstalled:
                        suggestions = codes
                        completer = WordCompleter(suggestions, ignore_case=True)
                        userInput = self.terminal_watson_translate_to_language_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()

                    if userInput in suggestions:
                        toLanguage = userInput

                    if runOnCopiedText:
                        userInput = clipboardText
                    else:
                        print(self.divider)
                        print("Enter the text you want to translate:")
                        userInput = self.simplePrompt(multiline=True)

                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    # translate if all input are invalid
                    command = f"TRANSLATE:::{fromLanguage}-{toLanguage}:::{userInput}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
                else:
                    return self.printInvalidOptionEntered()
            except:
                return self.printInvalidOptionEntered()
        else:
            print("Package 'ibm-watson' is not found on your system!")
            return ""

    def googleTranslate(self, runOnCopiedText=True):
        if config.isTranslateInstalled:
            if runOnCopiedText:
                clipboardText = self.getclipboardtext()
            try:
                if config.isPrompt_toolkitInstalled:
                    from prompt_toolkit.completion import WordCompleter

                codes = []
                display = []
                for key, value in Languages.googleTranslateCodes.items():
                    display.append(f"[<ref>{value}</ref> ] {key}")
                    codes.append(value)
                display = "<br>".join(display)
                display = TextUtil.htmlToPlainText(f"<h2>Languages</h2>{display}")

                print(self.divider)
                print(display)
                print("Translate from:")
                print("(enter a language code)")
                if config.isPrompt_toolkitInstalled:
                    suggestions = codes
                    completer = WordCompleter(suggestions, ignore_case=True)
                    userInput = self.terminal_google_translate_from_language_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in suggestions:
                    fromLanguage = userInput

                    print(self.divider)
                    print(display)
                    print("Translate to:")
                    print("(enter a language code)")
                    if config.isPrompt_toolkitInstalled:
                        suggestions = codes
                        completer = WordCompleter(suggestions, ignore_case=True)
                        userInput = self.terminal_google_translate_to_language_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()

                    if userInput in suggestions:
                        toLanguage = userInput

                    if runOnCopiedText:
                        userInput = clipboardText
                    else:
                        print(self.divider)
                        print("Enter the text you want to translate:")
                        userInput = self.simplePrompt(multiline=True)

                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    # translate if all input are invalid
                    from translate import Translator
                    translator= Translator(from_lang=fromLanguage, to_lang=toLanguage)
                    return translator.translate(userInput)
                else:
                    return self.printInvalidOptionEntered()
            except:
                return self.printInvalidOptionEntered()
        else:
            print("Package 'translate' is not found on your system!")
            return ""

    def printMultineNote(self):
        print("[Attention! Multiline input is enabled. Press Escape+Enter when you finish text entry.]")

    def getclipboardtext(self):
        try:
            if config.terminalEnableTermuxAPI:
                clipboardText = self.getCliOutput("termux-clipboard-get")
            elif config.isPyperclipInstalled:
                import pyperclip
                clipboardText = pyperclip.paste()
            if clipboardText:
                print(self.divider)
                print("Clipboard text:")
                print(clipboardText)
                print(self.divider)
                return clipboardText
            else:
                print("No copied text is found!")
                return self.cancelAction()
        except:
            return self.noClipboardUtility()

    def runclipboardtext(self, commandPrefix="", commandSuffix=""):
        clipboardText = self.getclipboardtext()
        if clipboardText:
            command = f"{commandPrefix}{clipboardText}{commandSuffix}"
            self.printRunningCommand(command)
            return self.getContent(command)
        else:
            return ""

    def bible(self):
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        return self.getContent(f"BIBLE:::{config.mainText}:::{bibleReference}")

    def commentary(self):
        bibleReference = self.textCommandParser.bcvToVerseReference(config.commentaryB, config.commentaryC, config.commentaryV)
        return self.getContent(f"COMMENTARY:::{config.commentaryText}:::{bibleReference}")

    def getCommand(self, command=""):
        if not command:
            command = self.command
        exception = "^(_setconfig:::|mp3:::|mp4:::|cmd:::|read:::|readsync:::)"
        if command.startswith(".") or re.search(exception, command.lower()):
            command = ".bible"
        return command

    # open web version
    # use local http-server if it is running
    # otherwise, use public
    def web(self, command="", filterCommand=True):
        server = "http://localhost:8080"
        if not self.isUrlAlive(server):
            server = ""
        weblink = TextUtil.getWeblink(self.getCommand(command) if filterCommand else command, server=server)
        return self.getContent(f"_website:::{weblink}")

    def isBibleReference(self, text):
        references = self.textCommandParser.extractAllVerses(text)
        return True if references else False

    def openbibleaudio(self):
        print(self.divider)
        self.printOptionsDisplay(self.crossPlatform.bibleAudioModules, "Installed Bible Audio")
        print(self.divider)
        try:
            print("Enter a number")
            userInput = self.simplePrompt(True)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if -1 < int(userInput) < len(self.crossPlatform.bibleAudioModules):
                module = self.crossPlatform.bibleAudioModules[int(userInput)]
                print(f"You selected '{module}'.")
                print("Enter bible reference(s) below:")
                userInput = self.simplePrompt()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if self.isBibleReference(userInput):
                    command = f"READ:::{module}:::{userInput}"
                    return self.getContent(command)
                else:
                    return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openmaps(self):
        print(self.divider)
        print("Enter bible reference(s) below:")
        print("(e.g. Rev 1:11, Josh 10:1-43, Act 15:36-18:22, etc.)")
        userInput = self.simplePrompt()
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        if self.isBibleReference(userInput):
            return self.web(f"MAP:::{userInput}", False)
        else:
            self.printInvalidOptionEntered()

    def share(self, command=""):
        try:
            weblink = TextUtil.getWeblink(self.getCommand(command))
            if config.terminalEnableTermuxAPI:
                plainText = self.getPlainText()
                plainText += f"\n\n{weblink}"
                plainText += "\n\n[Unique Bible App]"
                pydoc.pipepager(plainText, cmd="termux-share -a send")
                return ""
            else:
                import pyperclip
                pyperclip.copy(weblink)
            print(f"The following link is copied to clipboard:\n")
            print(weblink)
            print("\nOpen it in a web browser or share with others.")
            return ""
        except:
            return self.noClipboardUtility()

    def copy(self, content=""):
        try:
            if not content:
                content = self.getPlainText()
            if config.terminalEnableTermuxAPI:
                pydoc.pipepager(content, cmd="termux-clipboard-set")
            else:
                import pyperclip
                pyperclip.copy(content)
                print("Content is copied to clipboard.")
            return ""
        except:
            return self.noClipboardUtility()

    def copyHtml(self):
        try:
            if config.terminalEnableTermuxAPI:
                pydoc.pipepager(self.html, cmd="termux-clipboard-set")
            else:
                import pyperclip
                pyperclip.copy(self.html)
                print("HTML content is copied to clipboard.")
            return ""
        except:
            return self.noClipboardUtility()

    def noClipboardUtility(self):
        print("Clipboard utility is not found!")
        return ""

    def find(self):
        print("Enter a search pattern: ")
        userInput = self.terminal_find_session.prompt(self.inputIndicator, style=self.promptStyle).strip() if config.isPrompt_toolkitInstalled else input(self.inputIndicator).strip()
        if config.isColoramaInstalled:
            from colorama import init
            init()
            from colorama import Fore, Back, Style
            content = re.sub(r"({0})".format(userInput), r"{0}{1}\1{2}".format(Back.RED, Fore.WHITE, Style.RESET_ALL), self.plainText, flags=re.IGNORECASE)
        else:
            content = re.sub(r"({0})".format(userInput), r"[[[ \1 ]]]", self.plainText, flags=re.IGNORECASE)
        return content

    def history(self):
        return self.readPlainTextFile(os.path.join("terminal_history", "commands"))

    def latestchanges(self):
        return self.readPlainTextFile("latest_changes.txt")

    def readPlainTextFile(self, filename):
        if os.path.isfile(filename):
            with open(filename, "r", encoding="utf-8") as input_file:
                text = input_file.read()
        return self.keepContent(text)

    def displayMessage(self, message="", title="UniqueBible"):
        print(title)
        print(message)

    def printNoSupportMessage(self):
        print("This feature is not supported on your system!")
        return ""

    def buildPortablePython(self):
        if config.isPickleyInstalled:
            if not WebtopUtil.isPackageInstalled("portable-python"):
                os.system("pickley install portable-python")
            try:
                if WebtopUtil.isPackageInstalled("portable-python") and WebtopUtil.isPackageInstalled("tar"):
                    major, minor, micro, *_ = sys.version_info
                    thisdir = os.path.join("portable_python", "{0}_{1}.{2}.{3}".format(platform.system(), major, minor, micro))
                    if not os.path.isdir(thisdir):
                        os.makedirs(thisdir, exist_ok=True)
                    # build
                    os.system(f"cd {thisdir}; portable-python build {major}.{minor}.{micro}")
                    # unpack
                    print("Unpacking ...")
                    os.system(f"cd {thisdir}; tar -xf dist/*.tar.gz")
                    print("Done!")
                    portablePythonPath = os.path.join(thisdir, f"{major}.{minor}.{micro}", "bin", f"python{major}.{minor}")
                    if os.path.isfile(portablePythonPath):
                        print(f"The path of the newly built portable-python path is:")
                        print(portablePythonPath)
                        print(self.divider)
                        self.saveBashScript("gui")
                        print(self.divider)
                        self.saveBashScript("terminal")
                else:
                    print("Install both 'portable-python' and 'tar' first!")
            except:
                self.printNoSupportMessage()
        else:
            print("Install 'pickley' first!")
        return ""

    def saveBashScript(self, mode):
        major, minor, micro, *_ = sys.version_info
        script = """#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${0}BASH_SOURCE[0]{1}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
$SCRIPT_DIR/portable_python/{2}_{3}.{4}.{5}/{3}.{4}.{5}/bin/python{3}.{4} uba.py {6}
""".format("{", "}", platform.system(), major, minor, micro, mode)
        filepath = f"uba_{mode}_{platform.system()}_{major}.{minor}.{micro}.sh"
        with open(filepath, "w", encoding="utf-8") as fileObj:
            fileObj.write(script)
        # add executable permissions
        try:
            os.chmod(filepath, 0o755)
        except:
            pass
        print(f"Created '{filepath}' for running UBA in {mode} mode.")

    def update(self, debug=False):
        try:
            try:
                os.system("git pull")
                return self.finishUpdate()
            except:
                # Old way to update
                requestObject = requests.get("{0}patches.txt".format(UpdateUtil.repository))
                for line in requestObject.text.split("\n"):
                    if line:
                        try:
                            version, contentType, filePath = literal_eval(line)
                            if version > config.version:
                                localPath = os.path.join(*filePath.split("/"))
                                if debug:
                                    print("{0}:{1}".format(version, localPath))
                                else:
                                    if contentType == "folder":
                                        if not os.path.isdir(localPath):
                                            os.makedirs(localPath, exist_ok=True)
                                    elif contentType == "file":
                                        requestObject2 = requests.get("{0}{1}".format(UpdateUtil.repository, filePath))
                                        with open(localPath, "wb") as fileObject:
                                            fileObject.write(requestObject2.content)
                                    elif contentType == "delete":
                                        try:
                                            if os.path.exists(localPath):
                                                os.remove(localPath)
                                        except:
                                            print("Could not delete {0}".format(localPath))
                        except Exception as e:
                            return self.updateFailed()

                return self.finishUpdate()
        except:
            return self.updateFailed()

    def updateFailed(self):
        print("Failed to update to the latest version.")
        if not config.internet:
            print("You may need to check your internet connection.")
        return ""

    def finishUpdate(self):
        # set executable files on macOS or Linux
        if not platform.system() == "Windows":
            for filename in ("uba.py", "main.py", "BibleVerseParser.py", "RegexSearch.py"):
                if os.path.isfile(filename):
                    os.chmod(filename, 0o755)
                # finish message
        config.lastAppUpdateCheckDate = str(DateUtil.localDateNow())

        print("You have the latest version.")
        return ".restart"

    def config(self):
        intro = "<h2>Unique Bible App Configurations</h2>"
        intro += "<p>Default settings are good for general use.  In case you want to make changes, you may run '<ref>_setconfig:::</ref>' command in terminal mode.  Alternately, you may manually edit the file 'config.py', located in UBA home directory, when UBA is not running.</p>"
        self.html = "{0}<p>{1}</p>".format(intro, "</p><p>".join(["[ITEM] <ref>{0}</ref>{1}\nCurrent value: <z>{2}</z>".format(key, re.sub("        # ", "", value), eval("pprint.pformat(config."+key+")")) for key, value in config.help.items()]))
        self.plainText = TextUtil.htmlToPlainText(self.html).strip()
        return self.plainText

    def latestBible(self):
        command = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        self.printRunningCommand(command)
        return self.getContent(command)

    def backward(self):
        newChapter = config.mainC - 1
        if newChapter < 1:
            newChapter = 1
        command = self.textCommandParser.bcvToVerseReference(config.mainB, newChapter, 1)
        self.printRunningCommand(command)
        return self.getContent(command)

    def forward(self):
        newChapter = config.mainC
        if config.mainC < BibleBooks.getLastChapter(config.mainB):
            newChapter += 1
        command = self.textCommandParser.bcvToVerseReference(config.mainB, newChapter, 1)
        self.printRunningCommand(command)
        return self.getContent(command)

    def noPromptToolkit(self):
        print("Install package 'prompt_toolkit' first!")
        return ""

    def simplePrompt(self, numberOnly=False, multiline=False):
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            from util.PromptValidator import NumberValidator
            if numberOnly:
                if multiline:
                    self.printMultineNote()
                userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), multiline=multiline).strip()
            else:
                userInput = prompt(self.inputIndicator, style=self.promptStyle, multiline=multiline).strip()
        else:
            userInput = input(self.inputIndicator).strip()
        return userInput

    def isUrlAlive(self, url):
        #print(urllib.request.urlopen("https://www.stackoverflow.com").getcode())
        try:
            request = requests.get(url, timeout=5)
        except:
            return False
        return True if request.status_code == 200 else False

    def starthttpserver(self):
        url = "http://localhost:8080"
        if self.isUrlAlive(url):
            print(f"'{url}' is already alive!")
        else:
            subprocess.Popen([sys.executable, config.httpServerUbaFile, "http-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("UBA hptt-server started!")
        print("To connect, open 'http://{0}:{1}' in a web browser.".format(NetworkUtil.get_ip(), config.httpServerPort))
        return ""

    def stophttpserver(self):
        url = "http://localhost:8080/index.html?cmd=.stop"
        if self.isUrlAlive(url):
            print("http-server stopped!")
        else:
            print("http-server is not running!")
        return ""

    def downloadyoutube(self):
        if config.isYoutubeDownloaderInstalled and self.textCommandParser.isFfmpegInstalled():
            try:
                print(self.divider)
                print("Enter a youtube link:")
                userInput = self.simplePrompt()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                print("Checking connection ...")
                if self.isUrlAlive(userInput):
                    print("Connection is available.")
                    print(self.divider)
                    url = userInput
                    options = {
                        "0": "mp3:::",
                        "1": "mp4:::",
                    }
                    self.printChooseItem()
                    print("[0] Download mp3 audio")
                    print("[1] Download mp4 video")
                    userInput = self.simplePrompt()
                    if userInput in options:
                        command = f"{options[userInput]}{url}"
                        self.printRunningCommand(command)
                        return self.getContent(command)
                    else:
                        return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
            except:
                return self.printInvalidOptionEntered()
        self.printToolNotFound("yt-dlp' or 'ffmpeg")
        return ""

    def opentext(self):
        if config.isTextractInstalled:
            print(self.divider)
            print("Enter a file path below:")
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                userInput = prompt(self.inputIndicator, style=self.promptStyle).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if os.path.isfile(userInput):
                import textract
                return textract.process(userInput).decode()
            else:
                return self.printInvalidOptionEntered()
        self.printToolNotFound("textract")
        return ""

    def printToolNotFound(self, tool):
        print(f"Tool '{tool}' is not found on your system!")

    def opendata(self):
        try:
            print(self.divider)
            self.printOptionsDisplay(self.crossPlatform.dataList, "Bible Data")
            print(self.divider)
            print("Enter a number:")
            userInput = self.simplePrompt(True)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if int(userInput) in range(len(self.crossPlatform.dataList)):
                command = f"DATA:::{self.crossPlatform.dataList[int(userInput)]}"
                self.printRunningCommand(command)
                return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openTools2(self, moduleType):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
            elements = {
                "parallels": ("SEARCHBOOK:::Harmonies_and_Parallels:::", "BOOK:::Harmonies_and_Parallels", "BOOK:::Harmonies_and_Parallels:::"),
                "promises": ("SEARCHBOOK:::Bible_Promises:::", "BOOK:::Bible_Promises", "BOOK:::Bible_Promises:::"),
                "names": ("SEARCHTOOL:::HBN:::", "SEARCHTOOL:::HBN:::", ""),
                "characters": ("SEARCHTOOL:::EXLBP:::", "SEARCHTOOL:::EXLBP:::", "EXLB:::exlbp:::"),
                "locations": ("SEARCHTOOL:::EXLBL:::", "SEARCHTOOL:::EXLBL:::", "EXLB:::exlbl:::"),
            }
            *_, showAll, openPrefix = elements[moduleType]
            print(self.divider)
            command = showAll
            self.printRunningCommand(command)
            print(self.divider)
            content = self.getContent(command)
            if content.startswith("[MESSAGE]"):
                content = content[10:]
            if openPrefix:
                print(content)
                print(self.divider)
                print(f"Enter an item to open:")
                if config.isPrompt_toolkitInstalled:
                    userInput = prompt(self.inputIndicator, style=self.promptStyle).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                print(self.divider)
                command = f"{openPrefix}{userInput}"
                self.printRunningCommand(command)
                print(self.divider)
                return self.getContent(command)
            else:
                return content
        except:
            return self.printInvalidOptionEntered()

    def searchTools2(self, moduleType):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
            elements = {
                "parallels": ("SEARCHBOOK:::Harmonies_and_Parallels:::", "BOOK:::Harmonies_and_Parallels", "BOOK:::Harmonies_and_Parallels:::"),
                "promises": ("SEARCHBOOK:::Bible_Promises:::", "BOOK:::Bible_Promises", "BOOK:::Bible_Promises:::"),
                "names": ("SEARCHTOOL:::HBN:::", "SEARCHTOOL:::HBN:::", ""),
                "characters": ("SEARCHTOOL:::EXLBP:::", "SEARCHTOOL:::EXLBP:::", "EXLB:::exlbp:::"),
                "locations": ("SEARCHTOOL:::EXLBL:::", "SEARCHTOOL:::EXLBL:::", "EXLB:::exlbl:::"),
            }
            searchPrefix, showAll, openPrefix = elements[moduleType]
            print(self.divider)
            self.printSearchEntryPrompt()
            if config.isPrompt_toolkitInstalled:
                userInput = prompt(self.inputIndicator, style=self.promptStyle).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            elif not userInput:
                command = showAll
            else:
                command = f"{searchPrefix}{userInput}"
            self.printRunningCommand(command)
            print(self.divider)
            content = self.getContent(command)
            if content.startswith("[MESSAGE]"):
                content = content[10:]
            if openPrefix:
                print(content)
                print(self.divider)
                print(f"Enter an item to open:")
                if config.isPrompt_toolkitInstalled:
                    userInput = prompt(self.inputIndicator, style=self.promptStyle).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                print(self.divider)
                command = f"{openPrefix}{userInput}"
                self.printRunningCommand(command)
                print(self.divider)
                return self.getContent(command)
            else:
                return content
        except:
            return self.printInvalidOptionEntered()

    def quickedit(self, runOnCopiedText=True):
        try:
            if runOnCopiedText:
                self.getclipboardtext()
            options = {
                "0": ("Bible Book Notes", "EDITBOOKNOTE", ""),
                "1": ("Bible Chapter Notes", "EDITCHAPTERNOTE", ""),
                "2": ("Bible Verse Notes", "EDITVERSENOTE", ""),
                "3": ("Journals", "EDITJOURNAL", ""),
            }
            display = [f"[<ref>{key}</ref> ] {value[0]} - {value[-1]}" for key, value in options.items()]
            display = "<br>".join(display)
            display = f"<h2>Quick Open Copied Entry in Editor</h2>{display}" if runOnCopiedText else f"<h2>Quick Edit</h2>{display}"
            print(TextUtil.htmlToPlainText(display))
            print(self.divider)
            print("Enter a number:")
            userInput = self.simplePrompt(True)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if -1 < int(userInput) < 4:
                *_, openKeyword, latestSelection = options[userInput]
                latestSelection = f"{latestSelection}:::" if latestSelection else ""
                openPrefix = f"{openKeyword}:::{latestSelection}"
                if runOnCopiedText:
                    print(self.runclipboardtext(openPrefix))
                    return ""
                else:
                    print(self.divider)
                    #print("Type in an entry:")
                    print("Enter a day in yyyy-mm-dd format:" if openKeyword == "EDITJOURNAL" else "Enter a bible reference:")
                    userInput = self.simplePrompt()
                    command = f"{openPrefix}{userInput}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def quickopen(self, runOnCopiedText=True):
        try:
            if runOnCopiedText:
                self.getclipboardtext()
            options = {
                "0": ("Bible Version", "TEXT", ""),
                "1": ("Reference in Selected Bible", "BIBLE", config.mainText),
                "2": ("Reference in Favourite Bible", "BIBLE", self.getPlusBible()[2:]),
                "3": ("Reference in Hebrew & Green Bible", "BIBLE", config.favouriteOriginalBible),
                "4": ("Commentary Module", "COMMENTARY", ""),
                "5": ("Reference in Commentary", "COMMENTARY", config.commentaryText),
                "6": ("Bible Book Notes", "OPENBOOKNOTE", ""),
                "7": ("Bible Chapter Notes", "OPENCHAPTERNOTE", ""),
                "8": ("Bible Verse Notes", "OPENVERSENOTE", ""),
                "9": ("Journals", "OPENJOURNAL", ""),
                "10": ("Bible Audio", "READ", ""),
                "11": ("Bible Maps", "MAP", ""),
                "12": ("Chapter Overview", "OVERVIEW", ""),
                "13": ("Chapter Summary", "SUMMARY", ""),
                "14": ("Chapter Index", "CHAPTERINDEX", ""),
                "15": ("Verse Index", "INDEX", ""),
                "16": ("Cross-reference", "CROSSREFERENCE", ""),
                "17": ("Bible Version Comparison", "COMPARE", ""),
                "18": ("Bible Version Differences", "DIFFERENCE", ""),
                "19": ("Treasury of Scripture Knowledge (Enhanced)", "TSKE", ""),
                "20": ("Original Words", "WORDS", ""),
                "21": ("Original Word Translation", "TRANSLATION", ""),
                "22": ("Discourse Features", "DISCOURSE", ""),
                "23": ("Words, Translation & Discourse Combo", "COMBO", ""),
                "24": ("Bible Topics", "EXLB", "exlbt"),
                "25": ("Bible Encyclopedia", "ENCYCLOPEDIA", config.encyclopedia),
                "26": ("Bible Dictionary", "DICTIONARY", ""),
                "27": ("Third-party dictionary", "THIRDDICTIONARY", config.thirdDictionary),
                "28": ("Bible Parallels", "BOOK", "Harmonies_and_Parallels"),
                "29": ("Bible Promises", "BOOK", "Bible_Promises"),
                "30": ("Bible Characters", "EXLB", "exlbp"),
                "31": ("Bible Locations", "EXLB", "exlbl"),
                "32": ("Reference Book", "BOOK", config.book),
                "33": ("Bible Lexicon Entries", "LEXICON", config.lexicon),
                "34": ("Bible Lexicon Content", "REVERSELEXICON", config.lexicon),
                "35": ("Bible Concordance", "CONCORDANCE", config.concordance),
            }
            display = [f"[<ref>{key}</ref> ] {value[0]} - {value[-1]}" for key, value in options.items()]
            display = "<br>".join(display)
            display = f"<h2>Quick Open Copied Text in ...</h2>{display}" if runOnCopiedText else f"<h2>Quick Open</h2>{display}"
            print(TextUtil.htmlToPlainText(display))
            print(self.divider)
            print("Enter a number:")
            userInput = self.simplePrompt(True)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if userInput in options:
                *_, openKeyword, latestSelection = options[userInput]
                latestSelection = f"{latestSelection}:::" if latestSelection else ""
                if openKeyword == "COMMENTARY":
                    latestSelection = ":::"
                openPrefix = f"{openKeyword}:::{latestSelection}"
                if runOnCopiedText:
                    print(self.runclipboardtext(openPrefix))
                    return ""
                else:
                    print(self.divider)
                    print("Type in an entry:")
                    userInput = self.simplePrompt()
                    command = f"{openPrefix}{userInput}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def quickSearch(self, runOnCopiedText=True):
        try:
            if runOnCopiedText:
                self.getclipboardtext()
            searchModes = ("SEARCH", "SEARCHALL", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
            options = {
                "0": ("Whole Bible", searchModes[config.bibleSearchMode], "", config.mainText, ""),
                "1": ("Old Testament", searchModes[config.bibleSearchMode], "", config.mainText, ":::OT"),
                "2": ("New Testament", searchModes[config.bibleSearchMode], "", config.mainText, ":::NT"),
                "3": (self.bibleBooks.getStandardBookFullName(config.mainB), searchModes[config.bibleSearchMode], "", config.mainText, f":::{self.bibleBooks.getStandardBookAbbreviation(config.mainB)}"),
                "4": ("Bible Book Notes", "SEARCHBOOKNOTE", "OPENBOOKNOTE", "", ""),
                "5": ("Bible Chapter Notes", "SEARCHCHAPTERNOTE", "OPENCHAPTERNOTE", "", ""),
                "6": ("Bible Verse Notes", "SEARCHVERSENOTE", "OPENVERSENOTE", "", ""),
                "7": ("Journals", "SEARCHJOURNAL", "OPENJOURNAL", "", ""),
                "8": ("Bible Topics", "SEARCHTOOL", "EXLB", "EXLBT", ""),
                "9": ("Bible Encyclopedia", "SEARCHTOOL", "ENCYCLOPEDIA", config.encyclopedia, ""),
                "10": ("Bible Dictionary", "SEARCHTOOL", "DICTIONARY", config.dictionary, ""),
                "11": ("Third-party dictionary", "SEARCHTHIRDDICTIONARY", "THIRDDICTIONARY", config.thirdDictionary, ""),
                "12": ("Bible Parallels", "SEARCHBOOK", "BOOK", "Harmonies_and_Parallels", ""),
                "13": ("Bible Promises", "SEARCHBOOK", "BOOK", "Bible_Promises", ""),
                "14": ("Bible Names", "SEARCHTOOL", "", "HBN", ""),
                "15": ("Bible Characters", "SEARCHTOOL", "EXLB", "EXLBP", ""),
                "16": ("Bible Locations", "SEARCHTOOL", "EXLB", "EXLBL", ""),
                "17": ("Reference Book", "SEARCHBOOK", "BOOK", config.book, ""),
                "18": ("Bible Lexicon Entries", "SEARCHLEXICON", "LEXICON", config.lexicon, ""),
                "19": ("Bible Lexicon Content", "REVERSELEXICON", "", config.lexicon, ""),
                "20": ("Bible Concordance", "CONCORDANCE", "", config.concordance, ""),
            }
            display = [f"[<ref>{key}</ref> ] {value[0]} - {value[-2]}" for key, value in options.items()]
            display = "<br>".join(display)
            display = f"<h2>Quick Search Copied Text in ...</h2>{display}" if runOnCopiedText else f"<h2>Quick Search</h2>{display}"
            print(TextUtil.htmlToPlainText(display))
            print(self.divider)
            print("Enter a number:")
            userInput = self.simplePrompt(True)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if -1 < int(userInput) < 21:
                feature, searchKeyword, openKeyword, latestSelection, searchSuffix = options[userInput]
                latestSelection = f"{latestSelection}:::" if latestSelection else ""
                searchPrefix = f"{searchKeyword}:::{latestSelection}"
                if feature == "Bible Dictionary":
                    latestSelection = ""
                if openKeyword == "EXLB":
                    latestSelection = latestSelection.lower()
                config.terminalCommandDefault = f"{openKeyword}:::{latestSelection}" if openKeyword else ""
                if openKeyword:
                    if runOnCopiedText:
                        print(self.runclipboardtext(searchPrefix, searchSuffix))
                        return ""
                    else:
                        print(self.divider)
                        print("Enter a search item:")
                        userInput = self.simplePrompt()
                        command = f"{searchPrefix}{userInput}{searchSuffix}"
                        self.printRunningCommand(command)
                        print(self.getContent(command))
                        return ""
                else:
                    if runOnCopiedText:
                        return self.runclipboardtext(searchPrefix, searchSuffix)
                    else:
                        print(self.divider)
                        print("Enter a search item:")
                        userInput = self.simplePrompt()
                        command = f"{searchPrefix}{userInput}{searchSuffix}"
                        self.printRunningCommand(command)
                        return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def searchTools(self, moduleType, showModules):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter
            elements = {
                "BOOK": (config.book, self.crossPlatform.referenceBookList, config.bookChapter, self.terminal_books_selection_session, "SEARCHBOOK"),
                "TOPICS": (config.topic, self.crossPlatform.topicListAbb, config.topicEntry, self.terminal_topics_selection_session, ""),
                "ENCYCLOPEDIA": (config.encyclopedia, self.crossPlatform.encyclopediaListAbb, config.encyclopediaEntry, self.terminal_encyclopedia_selection_session, ""),
                "DICTIONARY": (config.dictionary, self.crossPlatform.dictionaryListAbb, config.dictionaryEntry, self.terminal_dictionary_selection_session, ""),
                "THIRDDICTIONARY": (config.thirdDictionary, self.crossPlatform.thirdPartyDictionaryList, config.thirdDictionaryEntry, self.terminal_thridPartyDictionaries_selection_session, "SEARCHTHIRDDICTIONARY"),
                "LEXICON": (config.lexicon, self.crossPlatform.lexiconList, config.lexiconEntry, self.terminal_lexicons_selection_session, "SEARCHLEXICON"),
                "REVERSELEXICON": (config.lexicon, self.crossPlatform.lexiconList, "", self.terminal_lexicons_selection_session, "REVERSELEXICON"),
            }
            print(self.divider)
            print(showModules())
            default, abbList, latestEntry, historySession, searchKeyword = elements[moduleType]
            if not searchKeyword:
                searchKeyword = "SEARCHTOOL"
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(abbList, ignore_case=True)
                userInput = historySession.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=default).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in abbList:
                module = userInput
                print(self.divider)
                self.printSearchEntryPrompt()
                if config.isPrompt_toolkitInstalled:
                    userInput = prompt(self.inputIndicator, style=self.promptStyle).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                command = f"{searchKeyword}:::{module}:::{userInput}"
                self.printRunningCommand(command)
                print(self.divider)
                content = self.getContent(command)
                if moduleType == "REVERSELEXICON":
                    return content
                print(content[10:] if content.startswith("[MESSAGE]") else content)
                print(self.divider)
                print(f"To open, enter a module entry (e.g. {latestEntry}):")
                if config.isPrompt_toolkitInstalled:
                    userInput = prompt(self.inputIndicator, style=self.promptStyle).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                print(self.divider)

                if moduleType == "TOPICS":
                    command = f"EXLB:::exlbt:::{userInput}"
                elif moduleType == "DICTIONARY":
                    command = f"{moduleType}:::{userInput}"
                else:
                    command = f"{moduleType}:::{module}:::{userInput}"
                self.printRunningCommand(command)
                return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def openTools(self, moduleType, showModules):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter
            elements = {
                "TOPICS": (config.topic, self.crossPlatform.topicListAbb, config.topicEntry, self.terminal_topics_selection_session, ""),
                "ENCYCLOPEDIA": (config.encyclopedia, self.crossPlatform.encyclopediaListAbb, config.encyclopediaEntry, self.terminal_encyclopedia_selection_session, ""),
                "DICTIONARY": (config.dictionary, self.crossPlatform.dictionaryListAbb, config.dictionaryEntry, self.terminal_dictionary_selection_session, ""),
                "THIRDDICTIONARY": (config.thirdDictionary, self.crossPlatform.thirdPartyDictionaryList, config.thirdDictionaryEntry, self.terminal_thridPartyDictionaries_selection_session, "SEARCHTHIRDDICTIONARY"),
                "LEXICON": (config.lexicon, self.crossPlatform.lexiconList, config.lexiconEntry, self.terminal_lexicons_selection_session, "SEARCHLEXICON"),
            }
            print(self.divider)
            print(showModules())
            default, abbList, latestEntry, historySession, searchKeyword = elements[moduleType]
            if not searchKeyword:
                searchKeyword = "SEARCHTOOL"
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(abbList, ignore_case=True)
                userInput = historySession.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=default).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in abbList:
                module = userInput
                print(self.divider)
                command = f"{searchKeyword}:::{module}:::"
                self.printRunningCommand(command)
                print(self.divider)
                content = self.getContent(command)
                if moduleType == "REVERSELEXICON":
                    return content
                print(content[10:] if content.startswith("[MESSAGE]") else content)
                print(self.divider)
                print(f"To open, enter a module entry (e.g. {latestEntry}):")
                if config.isPrompt_toolkitInstalled:
                    userInput = prompt(self.inputIndicator, style=self.promptStyle).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                print(self.divider)

                if moduleType == "TOPICS":
                    command = f"EXLB:::exlbt:::{userInput}"
                elif moduleType == "DICTIONARY":
                    command = f"{moduleType}:::{userInput}"
                else:
                    command = f"{moduleType}:::{module}:::{userInput}"
                self.printRunningCommand(command)
                return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def openreferencebook(self):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showreferencebooks())
            print(self.divider)
            print("Enter a reference book:")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.referenceBookList, ignore_case=True)
                userInput = self.terminal_books_selection_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=config.book).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.crossPlatform.referenceBookList:
                book = userInput
                chapterList = Book(book).getTopicList()
                chapterDisplay = "<h2>Chapters</h2>"
                chapterDisplay += "<br>".join([f"<ref>{chapter}</ref>" for chapter in chapterList])
                print(self.divider)
                print(TextUtil.htmlToPlainText(chapterDisplay).strip())
                print(self.divider)
                print("Enter a chapter title:")
                if config.isPrompt_toolkitInstalled:
                    completer = WordCompleter(chapterList, ignore_case=True)
                    userInput = prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=config.bookChapter if config.bookChapter in chapterList else "").strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in chapterList:
                    command = f"BOOK:::{book}:::{userInput}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
                else:
                    return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def journalFeature(self, feature="OPENJOURNAL"):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
            today = date.today()
            print(self.divider)
            print(f"Enter a year, e.g. {today.year}:")
            if config.isPrompt_toolkitInstalled:
                userInput = prompt(self.inputIndicator, style=self.promptStyle, default=str(today.year)).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if int(userInput):
                year = userInput
                print(self.divider)
                print(f"Enter a month, e.g. {today.month}:")
                if config.isPrompt_toolkitInstalled:
                    userInput = prompt(self.inputIndicator, style=self.promptStyle, default=str(today.month)).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if int(userInput):
                    month = userInput
                    print(self.divider)
                    print(f"Enter a day, e.g. {today.day}:")
                    if config.isPrompt_toolkitInstalled:
                        userInput = prompt(self.inputIndicator, style=self.promptStyle, default=str(today.day)).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(userInput):
                        day = userInput
                        command = f"{feature}:::{year}-{month}-{day}"
                        self.printRunningCommand(command)
                        return self.getContent(command)
                    else:
                        return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openbiblemodulenote(self):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showbibles())
            print(self.divider)
            print("Enter a bible abbreviation:")
            print("(choose a bible module that contains notes)")
            # select bible or bibles
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.textList, ignore_case=True)
                defaultText = self.getDefaultText()
                userInput = self.terminal_bible_selection_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=defaultText).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.crossPlatform.textList:
                bible = userInput
                print(self.divider)
                print(self.showbibleabbreviations(text=bible))
                print(self.divider)
                self.printChooseItem()
                print("(enter a book number)")
                # select bible book
                if config.isPrompt_toolkitInstalled:
                    from util.PromptValidator import NumberValidator
                    completer = WordCompleter([str(i) for i in self.bookNumbers], ignore_case=True)
                    userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), completer=completer, default=str(config.mainB)).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if int(userInput) in self.bookNumbers:
                    print(userInput, self.bookNumbers)
                    bibleBookNumber = userInput
                    print(self.divider)
                    self.showbiblechapters(text=bible, b=bibleBookNumber)
                    print(self.divider)
                    self.printChooseItem()
                    print("(enter a chapter number)")
                    # select bible chapter
                    if config.isPrompt_toolkitInstalled:
                        from util.PromptValidator import NumberValidator
                        defaultChapter = str(config.mainC) if config.mainC in self.currentBibleChapters else str(self.currentBibleChapters[0])
                        userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=defaultChapter).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleChapters:
                        bibleChapter = userInput
                        print(self.divider)
                        self.showbibleverses(text=bible, b=bibleBookNumber, c=int(userInput))
                        print(self.divider)
                        self.printChooseItem()
                        print("(enter a verse number)")
                        # select verse number
                        if config.isPrompt_toolkitInstalled:
                            from util.PromptValidator import NumberValidator
                            defaultVerse = str(config.mainV) if config.mainV in self.currentBibleVerses else str(self.currentBibleVerses[0])
                            userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=defaultVerse).strip()
                        else:
                            userInput = input(self.inputIndicator).strip()
                        if not userInput or userInput.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        if int(userInput) in self.currentBibleVerses:
                            bibleVerse = userInput
                            command = f"_biblenote:::{bible}:::{bibleBookNumber}.{bibleChapter}.{bibleVerse}"
                            self.printRunningCommand(command)
                            return self.getContent(command)
                        else:
                            return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()


    def openversefeature(self, feature="CROSSREFERENCE"):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            firstBible = config.mainText
            print(self.divider)
            print(self.showbibleabbreviations(text=firstBible))
            print(self.divider)
            self.printChooseItem()
            print("(enter a book abbreviation)")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.currentBibleAbbs, ignore_case=True)
                userInput = prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=self.currentBibleAbb).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.currentBibleAbbs:
                abbIndex = self.currentBibleAbbs.index(userInput)
                bibleBookNumber = self.bookNumbers[abbIndex]
                bibleAbb = userInput
                print(self.divider)
                self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                print(self.divider)
                self.printChooseItem()
                print("(enter a chapter number)")
                if config.isPrompt_toolkitInstalled:
                    from util.PromptValidator import NumberValidator
                    defaultChapter = str(config.mainC) if config.mainC in self.currentBibleChapters else str(self.currentBibleChapters[0])
                    userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=defaultChapter).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if int(userInput) in self.currentBibleChapters:
                    bibleChapter = userInput
                    print(self.divider)
                    self.showbibleverses(text=firstBible, b=bibleBookNumber, c=int(userInput))
                    print(self.divider)
                    self.printChooseItem()
                    print("(enter a verse number)")
                    if config.isPrompt_toolkitInstalled:
                        from util.PromptValidator import NumberValidator
                        defaultVerse = str(config.mainV) if config.mainV in self.currentBibleVerses else str(self.currentBibleVerses[0])
                        userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=defaultVerse).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleVerses:
                        bibleVerse = userInput
                        command = f"{feature}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                        self.printRunningCommand(command)
                        return self.getContent(command)
                    else:
                        return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openchapterfeature(self, feature="OVERVIEW"):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            firstBible = config.mainText
            print(self.divider)
            print(self.showbibleabbreviations(text=firstBible))
            print(self.divider)
            self.printChooseItem()
            print("(enter a book abbreviation)")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.currentBibleAbbs, ignore_case=True)
                userInput = prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=self.currentBibleAbb).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.currentBibleAbbs:
                abbIndex = self.currentBibleAbbs.index(userInput)
                bibleBookNumber = self.bookNumbers[abbIndex]
                bibleAbb = userInput
                print(self.divider)
                self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                print(self.divider)
                self.printChooseItem()
                print("(enter a chapter number)")
                if config.isPrompt_toolkitInstalled:
                    from util.PromptValidator import NumberValidator
                    defaultChapter = str(config.mainC) if config.mainC in self.currentBibleChapters else str(self.currentBibleChapters[0])
                    userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=defaultChapter).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if int(userInput) in self.currentBibleChapters:
                    bibleChapter = userInput
                    command = f"{feature}:::{bibleAbb} {bibleChapter}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
                else:
                    return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openbookfeature(self, feature="introduction"):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            firstBible = config.mainText
            print(self.divider)
            print(self.showbiblebooks(text=firstBible))
            print(self.divider)
            self.printChooseItem()
            print("(enter a book abbreviation)")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.currentBibleBooks, ignore_case=True)
                userInput = prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=self.currentBibleBook).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.currentBibleBooks:
                #bookIndex = self.currentBibleBooks.index(userInput)
                #bibleBookNumber = self.bookNumbers[bookIndex]
                bibleBook = userInput
                features = {
                    "introduction": "SEARCHBOOKCHAPTER:::Tidwell_The_Bible_Book_by_Book",
                    "dictionary": f"SEARCHTOOL:::{config.dictionary}",
                    "encyclopedia": f"SEARCHTOOL:::{config.encyclopedia}",
                    "timelines": "SEARCHBOOKCHAPTER:::Timelines",
                }
                feature = features.get(feature, feature)
                command = f"{feature}:::{bibleBook}"
                self.printRunningCommand(command)
                return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openbible(self):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showbibles())
            print(self.divider)
            self.printChooseItem()
            print("Enter a bible abbreviation to open a single version, e.g. 'KJV'")
            print("To compare multiple versions, use '_' as a delimiter, e.g. 'KJV_NET_OHGBi'")
            # select bible or bibles
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.textList, ignore_case=True)
                defaultText = self.getDefaultText()
                userInput = self.terminal_bible_selection_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=defaultText).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if self.isValidBibles(userInput):
                bible = userInput
                firstBible = bible.split("_")[0]
                print(self.divider)
                print(self.showbibleabbreviations(text=firstBible))
                print(self.divider)
                self.printChooseItem()
                print("(enter a book abbreviation)")
                # select bible book
                if config.isPrompt_toolkitInstalled:
                    completer = WordCompleter(self.currentBibleAbbs, ignore_case=True)
                    userInput = prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=self.currentBibleAbb).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in self.currentBibleAbbs:
                    abbIndex = self.currentBibleAbbs.index(userInput)
                    bibleBookNumber = self.bookNumbers[abbIndex]
                    bibleAbb = userInput
                    print(self.divider)
                    self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                    print(self.divider)
                    self.printChooseItem()
                    print("(enter a chapter number)")
                    # select bible chapter
                    if config.isPrompt_toolkitInstalled:
                        from util.PromptValidator import NumberValidator
                        defaultChapter = str(config.mainC) if config.mainC in self.currentBibleChapters else str(self.currentBibleChapters[0])
                        userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=defaultChapter).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleChapters:
                        bibleChapter = userInput
                        print(self.divider)
                        self.showbibleverses(text=firstBible, b=bibleBookNumber, c=int(userInput))
                        print(self.divider)
                        self.printChooseItem()
                        print("(enter a verse number)")
                        # select verse number
                        if config.isPrompt_toolkitInstalled:
                            from util.PromptValidator import NumberValidator
                            defaultVerse = str(config.mainV) if config.mainV in self.currentBibleVerses else str(self.currentBibleVerses[0])
                            userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=defaultVerse).strip()
                        else:
                            userInput = input(self.inputIndicator).strip()
                        if not userInput or userInput.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        if int(userInput) in self.currentBibleVerses:
                            bibleVerse = userInput
                            # formulate UBA command
                            if "_" in bible:
                                command = f"COMPARE:::{bible}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                            else:
                                command = f"BIBLE:::{bible}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                            self.printRunningCommand(command)
                            return self.getContent(command)
                        else:
                            return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def whatis(self):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.commands())
            print(self.divider)
            self.printChooseItem()
            commands = self.getTextCommandSuggestion(False)
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(commands, ignore_case=True)
                userInput = self.terminal_bible_selection_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in commands:
                return self.whatiscontent(userInput)
        except:
            return self.printInvalidOptionEntered()

    def whatiscontent(self, command):
        if command in self.dotCommands:
            print(self.dotCommands[command][0])
        else:
            print(self.getContent(f"_whatis:::{command}"))
        return ""

    def searchconcordance(self):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showstrongbibles())
            self.printChooseItem()
            print("Enter a bible abbreviation to search a single version, e.g. 'KJVx'")
            print("To search multiple versions, use '_' as a delimiter, e.g. 'KJVx_RWVx_OHGBi'")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.strongBibles, ignore_case=True)
                userInput = self.terminal_search_strong_bible_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=config.concordance).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if self.isValidBibles(userInput):
                # bible version(s) defined
                bible = userInput
                print(self.divider)
                print("Enter a Strong's number or lexical entry:")
                userInput = self.simplePrompt()
                command = f"CONCORDANCE:::{bible}:::{userInput}"
                self.printRunningCommand(command)
                return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def searchbible(self):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showbibles())
            print(self.divider)
            self.printChooseItem()
            print("Enter a bible abbreviation to open a single version, e.g. 'KJV'")
            print("To compare multiple versions, use '_' as a delimiter, e.g. 'KJV_NET_OHGBi'")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.textList, ignore_case=True)
                defaultText = self.getDefaultText()
                userInput = self.terminal_bible_selection_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=defaultText).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if self.isValidBibles(userInput):
                # bible version(s) defined
                bible = userInput

                firstBible = bible.split("_")[0]
                print(self.divider)
                print(self.showbibleabbreviations(text=firstBible))
                print(self.divider)
                self.printChooseItem()
                print("(enter bible books for search)")
                print("(use ',' as a delimiter between books)")
                print("(use '-' as a range indicator)")
                print("(e.g. 'ALL', 'OT', 'NT', 'Gen, John', 'Matt-John, 1Cor, Rev', etc.)")
                # select bible book range
                if config.isPrompt_toolkitInstalled:
                    completer = WordCompleter(["ALL", "OT", "NT"] + self.currentBibleAbbs, ignore_case=True)
                    userInput = self.terminal_search_bible_book_range_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default="ALL").strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if BibleVerseParser(config.parserStandarisation).extractBookListAsString(userInput):
                    # define book range
                    bookRange = userInput

                    searchOptions = {
                        "SEARCH": ("search for occurrence of a string", "plain text", "Jesus love"),
                        "SEARCHALL": ("search for string", "plain text", "Jesus love"),
                        "ANDSEARCH": ("search for a combination of strings appeared in the same verse", "multiple plain text strings, delimited by '|'", "Jesus|love|disciple"),
                        "ORSEARCH": ("search for either one of the entered strings appeared in a single verse", "multiple plain text strings, delimited by '|'", "Jesus|love|disciple"),
                        "ADVANCEDSEARCH": ("search for a condition or a combination of conditions", "condition statement placed after the keyword 'WHERE' in a SQL query", 'Book = 1 AND Scripture LIKE "%worship%"'),
                        "REGEXSEARCH": ("search for a regular expression", "regular expression", "Jesus.*?love"),
                    }
                    searchOptionsList = list(searchOptions.keys())
                    print(self.divider)
                    display = "<br>".join([f"[<ref>{index}</ref> ] {searchOptions[item][0]}" for index, item in enumerate(searchOptionsList)])
                    display = f"<h2>Search Options</h2>{display}"
                    print(TextUtil.htmlToPlainText(display).strip())
                    print(self.divider)
                    self.printChooseItem()
                    print("(enter a number)")
                    if config.isPrompt_toolkitInstalled:
                        from util.PromptValidator import NumberValidator
                        userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=str(config.bibleSearchMode)).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    userInput = int(userInput)
                    if -1 < userInput < 6:
                        # define bibleSearchMode
                        config.bibleSearchMode = userInput
                        # define command keyword
                        keyword = searchOptionsList[userInput]
                        print(self.divider)
                        self.printSearchEntryPrompt()
                        *_, stringFormat, example = searchOptions[searchOptionsList[userInput]]
                        print(f"(format: {stringFormat})")
                        print(f"(example: {example})")
                        if config.isPrompt_toolkitInstalled:
                            userInput = self.terminal_search_bible_session.prompt(self.inputIndicator, style=self.promptStyle).strip()
                        else:
                            userInput = input(self.inputIndicator).strip()
                        if not userInput or userInput.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        command = f"{keyword}:::{bible}:::{userInput}:::{bookRange}"

                        # Check if it is a case-sensitive search
                        print(self.divider)
                        print("Case sensitive? ([y]es or [n]o)")
                        if config.isPrompt_toolkitInstalled:
                            userInput = prompt(self.inputIndicator, style=self.promptStyle, default="Y" if config.enableCaseSensitiveSearch else "N").strip()
                        else:
                            userInput = input(self.inputIndicator).strip()
                        if not userInput or userInput.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        if userInput.lower() in ("yes", "y", "no", "n"):
                            config.enableCaseSensitiveSearch = (userInput.lower()[0] == "y")
                            self.printRunningCommand(command)
                            return self.getContent(command)
                        else:
                            return self.printInvalidOptionEntered()
                    else:
                        return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def opencommentary(self):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showcommentaries())
            print(self.divider)
            self.printChooseItem()
            print("Enter a commentary abbreviation, e.g. 'CBSC'")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.commentaryList, ignore_case=True)
                defaultText = config.commentaryText
                userInput = self.terminal_commentary_selection_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=defaultText).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.crossPlatform.commentaryList:
                module = userInput
                firstBible = "KJV"
                print(self.divider)
                print(self.showbibleabbreviations(text=firstBible, commentary=True))
                print(self.divider)
                self.printChooseItem()
                print("(enter a book abbreviation)")
                if config.isPrompt_toolkitInstalled:
                    completer = WordCompleter(self.currentBibleAbbs, ignore_case=True)
                    userInput = prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=self.currentBibleAbb).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in self.currentBibleAbbs:
                    abbIndex = self.currentBibleAbbs.index(userInput)
                    bibleBookNumber = self.bookNumbers[abbIndex]
                    bibleAbb = userInput
                    print(self.divider)
                    self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                    print(self.divider)
                    self.printChooseItem()
                    print("(enter a chapter number)")
                    if config.isPrompt_toolkitInstalled:
                        from util.PromptValidator import NumberValidator
                        defaultChapter = str(config.commentaryC) if config.commentaryC in self.currentBibleChapters else str(self.currentBibleChapters[0])
                        userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=defaultChapter).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleChapters:
                        bibleChapter = userInput
                        print(self.divider)
                        self.showbibleverses(text=firstBible, b=bibleBookNumber, c=int(userInput))
                        print(self.divider)
                        self.printChooseItem()
                        print("(enter a verse number)")
                        if config.isPrompt_toolkitInstalled:
                            from util.PromptValidator import NumberValidator
                            defaultVerse = str(config.commentaryV) if config.commentaryV in self.currentBibleVerses else str(self.currentBibleVerses[0])
                            userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=defaultVerse).strip()
                        else:
                            userInput = input(self.inputIndicator).strip()
                        if not userInput or userInput.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        if int(userInput) in self.currentBibleVerses:
                            bibleVerse = userInput
                            command = f"COMMENTARY:::{module}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                            self.printRunningCommand(command)
                            return self.getContent(command)
                        else:
                            return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def getDefaultText(self):
        if config.mainText in self.crossPlatform.textList:
            defaultText = config.mainText
        elif config.favouriteBible in self.crossPlatform.textList:
            defaultText = config.favouriteBible
        elif config.favouriteBible2 in self.crossPlatform.textList:
            defaultText = config.favouriteBible2
        elif config.favouriteBible3 in self.crossPlatform.textList:
            defaultText = config.favouriteBible3
        else:
            defaultText = self.crossPlatform.textList[0]
        return defaultText

    def isValidBibles(self, userInput):
        if userInput:
            for bible in userInput.split("_"):
                if not bible in self.crossPlatform.textList:
                    return False
            return True
        return False

    def changecolors(self):
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            from prompt_toolkit.completion import WordCompleter

        optionMap = {
            "Terminal Heading Text Color": "terminalHeadingTextColor",
            "Terminal Verse Number Color": "terminalVerseNumberColor",
            "Terminal Resource Link Color": "terminalResourceLinkColor",
            "Terminal Verse Selection Background": "terminalVerseSelectionBackground",
            "Terminal Verse Selection Foreground": "terminalVerseSelectionForeground",
            "Terminal Search Highlight Background": "terminalSearchHighlightBackground",
            "Terminal Search Highlight Foreground": "terminalSearchHighlightForeground",
            "Terminal Find Highlight Background": "terminalFindHighlightBackground",
            "Terminal Find Highlight Foreground": "terminalFindHighlightForeground",
        }
        options = [f"[{i}] {item}" for i, item in enumerate(optionMap.keys())]
        print(self.divider)
        self.printChooseItem()
        print(pprint.pformat(options))
        print(self.divider)
        self.printEnterNumber((len(options) - 1))
        self.printCancelOption()
        if config.isPrompt_toolkitInstalled:
            completer = WordCompleter([str(i) for i in range(len(options))])
            userInput = prompt(self.inputIndicator, style=self.promptStyle, completer=completer)
        else:
            userInput = input(self.inputIndicator)
        if userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        try:
            optionIndex = int(userInput.strip())
            option = options[optionIndex]
            option = re.sub("^\[[0-9]+?\] ", "", option)
            configitem = optionMap[option]
            options = [f"[{i}] {item}" for i, item in enumerate(config.terminalColors)]
            print(self.divider)
            self.printChooseItem()
            print(pprint.pformat(options))
            print(self.divider)
            self.printEnterNumber((len(options) - 1))
            self.printCancelOption()
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter([str(i) for i in range(len(options))])
                userInput = prompt(self.inputIndicator, style=self.promptStyle, completer=completer)
            else:
                userInput = input(self.inputIndicator)
            if userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            else:
                color = config.terminalColors[int(userInput)]
                command = f"_setconfig:::{configitem}:::'{color}'"
                self.printRunningCommand(command)
                return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def swap(self):
        command = f"TEXT:::{(self.getPlusBible()[2:])}"
        self.printRunningCommand(command)
        return self.getContent(command)

    # Shared prompt message

    def toast(self, message):
        if config.terminalEnableTermuxAPI and config.terminalEnableTermuxAPIToast:
            self.getContent(f"cmd:::termux-toast -s {message}")

    def actionDone(self):
        message = "Done!"
        print(message)
        self.toast(message)
        return ""

    def downloadbibleaudio(self):
        options = list(self.crossPlatform.verseByVerseAudio.keys())
        print(self.divider)
        print(self.getOptionsDisplay(options, "Download Bible Audio"))
        print(self.divider)
        userInput = self.simplePrompt(True)
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        index = int(userInput)
        if index in range(len(options)):
            choice = options[index]
            print(f"You selected '{choice}'.")
            module, repo, *_ = self.crossPlatform.verseByVerseAudio[choice]
            self.downloadbibleaudioaction(module, repo)
        else:
            self.printInvalidOptionEntered()

    def downloadbibleaudioaction(self, module, repo):
        try:
            print(self.divider)
            audioDir = os.path.join(config.audioFolder, "bibles", module, "default")
            Path(audioDir).mkdir(parents=True, exist_ok=True)
            # remove old files
            if os.path.isdir(audioDir):
                # os.rmdir does not work with sub directories
                # os.rmdir(audioDir)
                # use shutil.rmtree instead
                shutil.rmtree(audioDir)
            os.system(f"git clone https://github.com/{repo} {audioDir}")
            print("Downloaded!")
            print("unpacking files ...")
            for item in os.listdir(audioDir):
                zipFile = os.path.join(audioDir, item)
                if os.path.isfile(zipFile) and item.endswith(".zip"):
                    #os.system(f"unzip {zipFile}")
                    # Unzip file
                    shutil.unpack_archive(zipFile, audioDir)
                    # Delete zip file
                    os.remove(zipFile)
            print("Installed!")
        except:
            print("Errors!")

    def cancelAction(self):
        config.terminalCommandDefault = ""
        message = "Action cancelled!"
        print(self.divider)
        print(message)
        self.toast(message)
        self.clipboardMonitorFeature()
        return ""

    def printChooseItem(self):
        print("Choose an item:")

    def printCancelOption(self):
        print(f"(or enter '{config.terminal_cancel_action}' to cancel)")

    def printInvalidOptionEntered(self):
        message = "Invalid option entered!"
        print(message)
        self.toast(message)
        return ""

    def printRunningCommand(self, command):
        self.command = command
        print(f"Running {command} ...")

    def printEnterNumber(self, number):
        print(f"Enter a number [0 ... {number}]:")

    # Get latest content in plain text
    def getPlainText(self, content=None):
        return TextUtil.htmlToPlainText(self.html if content is None else content, False).strip()

    def printSearchEntryPrompt(self):
        print("Enter a search item:")

    def searchNote(self, keyword="SEARCHBOOKNOTE"):
        try:
            print(self.divider)
            self.printSearchEntryPrompt()
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                userInput = prompt(self.inputIndicator, style=self.promptStyle).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            command = f"{keyword}:::{userInput}"
            self.printRunningCommand(command)
            return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def clipboardMonitorFeature(self):
        self.showClipboardMonitorStatus()
        if config.terminalEnableClipboardMonitor:
            # check English definition of selected word
            selectedText = self.getclipboardtext()
            if selectedText in HBN.entries:
                definition = HBN.entries[selectedText]
            else:
                definition = self.getDefinition(selectedText)
                if not definition:
                    lemma = config.lemmatizer.lemmatize(selectedText)
                    if lemma == selectedText:
                        lemma = ""
                    else:
                        lemma = f"{lemma} -"
                    definition = self.getDefinition(lemma)
                    if definition:
                        definition = "{0}{1}".format(lemma, definition)
                    elif config.isChineseEnglishLookupInstalled:
                        definition = "{0}{1}".format(lemma, config.cedict.lookup(lemma))
            print("Definition:")
            print(definition)
            print(self.divider)
            self.extract(selectedText)

    def getDefinition(self, entry):
        definition = ""
        synsets = config.wordnet.synsets(entry)
        if synsets:
            definition = synsets[0].definition()
        return definition

    def printOptionsDisplay(self, options, heading=""):
        print(self.getOptionsDisplay(options, heading))

    def getOptionsDisplay(self, options, heading=""):
        optionsDisplay = [f"[<ref>{i}</ref> ] {mode}" for i, mode in enumerate(options)]
        optionsDisplay = "<br>".join(optionsDisplay)
        if heading:
            optionsDisplay = f"<h2>{heading}</h2>{optionsDisplay}"
        return TextUtil.htmlToPlainText(optionsDisplay).strip()

    def changeDefaultCommand(self):
        try:
            print(self.divider)
            print("Change default command")
            print("(What is 'default command'?  \nUBA runs default command when users simply press Enter key in command prompt without text entry)\n")
            print("Current default command is:")
            print(config.terminalDefaultCommand)
            print(self.divider)
            options = (".menu", ".run", ".search", ".quicksearch", ".quicksearchcopiedtext", "[CUSTOMISE]")
            self.printOptionsDisplay(options, "Change Default Command")
            print(self.divider)
            print("Enter a number:")
            userInput = self.simplePrompt(True)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if userInput in ("0", "1", "2", "3", "4"):
                return self.getContent(f"_setconfig:::terminalDefaultCommand:::'{options[int(userInput)]}'")
            elif userInput == "5":
                print(self.divider)
                print("Enter an UBA command:")
                userInput = self.simplePrompt()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                return self.getContent(f"_setconfig:::terminalDefaultCommand:::'{userInput}'")
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def changemymenu(self):
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            print("Change My Menu")
            print("Enter a terminal command on each line:")
            print(self.divider)
            self.printMultineNote()
            default = "\n".join(config.terminalMyMenu)
            userInput = prompt(self.inputIndicator, style=self.promptStyle, multiline=True, default=default).strip()
            config.terminalMyMenu = [i.lower().strip() for i in userInput.split("\n") if i.lower().strip() in config.mainWindow.dotCommands]
            print("config.terminalMyMenu is changed to:")
            print(config.terminalMyMenu)
        else:
            return self.printMissingPackage("prompt_toolkit")
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()

    def changebiblesearchmode(self):
        try:
            print(self.divider)
            searchModes = ("SEARCH", "SEARCHALL", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
            self.printOptionsDisplay(searchModes, "Change default bible search mode")
            print(self.divider)
            print("Enter a number:")
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from util.PromptValidator import NumberValidator
                userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator(), default=str(config.bibleSearchMode)).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if userInput in ("0", "1", "2", "3", "4", "5"):
                return self.getContent(f"_setconfig:::bibleSearchMode:::{userInput}")
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def readHowTo(self, filename):
        filepath = os.path.join("terminal_mode", "how_to", f"{filename}.md")
        return self.readPlainTextFile(filepath)

    def changenoteeditor(self):
        try:
            print(self.divider)
            print("Select default note / journal editor:")
            editors = {
                "micro": "micro",
                "nano": "nano --softwrap --atblanks -",
                "vi": "vi -",
                "vim": "vim -",
            }
            configurablesettings = list(editors.keys())
            print(configurablesettings)
            print(self.divider)
            print("Enter your favourite text editor:")
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit.completion import WordCompleter
                from prompt_toolkit import prompt
                completer = WordCompleter(configurablesettings)
                userInput = prompt(self.inputIndicator, style=self.promptStyle, completer=completer).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if userInput in configurablesettings:
                #config.terminalNoteEditor = editors[userInput]
                return self.getContent(f"_setconfig:::terminalNoteEditor:::'{editors[userInput]}'")
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def fingerprint(self):
        try:
            output = json.loads(self.getCliOutput("termux-fingerprint"))
            return True if output["auth_result"] == "AUTH_RESULT_SUCCESS" else False
        except:
            return False

    def printTermuxApiDisabled(self):
        print("Termux API is not yet enabled!")
        print("This feature is available on Android ONLY!")
        print("Make sure both Termux:API app and termux-api package are installed first.")
        print("Then, run '.config' and set 'terminalEnableTermuxAPI' to True.")

    def sendFile(self, filepath):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
            self.getCliOutput(f"termux-share -a send {filepath}")
            self.actionDone()
        else:
            self.printTermuxApiDisabled()
        return ""

    def restoreFile(self, filepath):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
            self.getCliOutput(f"mv {filepath} {filepath}.bak")
            self.getCliOutput(f"termux-storage-get {filepath}")
            self.actionDone()
        else:
            self.printTermuxApiDisabled()
        return ""

    def restoreLastFile(self, filepath):
        if config.terminalEnableTermuxAPI:
            if os.path.isfile(f"{filepath}.bak"):
                if not self.fingerprint():
                    return self.cancelAction()
                self.getCliOutput(f"cp {filepath}.bak {filepath}")
                self.actionDone()
            else:
                print(f"Backup file '{filepath}.bak' does not exist!")
                return self.cancelAction()
        else:
            self.printTermuxApiDisabled()
        return ""

    def changeconfig(self, terminalCommandOnly=False):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
        try:
            print(self.divider)
            print("Configurable Settings:")
            print("(Caution! UBA may stop from working if you make invalid changes.)\n")
            # display configurable settings
            configurablesettings = [i for i in config.help.keys() if i.startswith("terminal")] if terminalCommandOnly else list(config.help.keys())
            displayContent = pprint.pformat(configurablesettings)
            print(displayContent)
            print(self.divider)
            print("Enter the item you want to change:")
            
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit.completion import WordCompleter
                completer = WordCompleter(configurablesettings, ignore_case=True)
                userInput = self.terminal_config_selection_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if userInput in configurablesettings:
                value = userInput
                print(self.divider)
                print(self.getContent(f"_setconfig:::{value}"))
                print(self.divider)
                print("Enter a value:")
                if config.isPrompt_toolkitInstalled:
                    from prompt_toolkit import prompt
                    userInput = prompt(self.inputIndicator, style=self.promptStyle).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                print(self.getContent(f"_setconfig:::{value}:::{userInput}"))
                return ".restart"
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def editConfig(self, editor):
        print(self.divider)
        print("Caution! Editing 'config.py' incorrectly may stop UBA from working.")
        print("Do you want to proceed? [y]es / [N]o")
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            userInput = prompt(self.inputIndicator, style=self.promptStyle, default="N").strip()
        else:
            userInput = input(self.inputIndicator).strip()
        userInput = userInput.lower()
        if userInput in ("n", "no"):
            return self.cancelAction()
        elif userInput in ("y", "yes"):
            print("reading config content ...")
            if os.path.isfile("config.py"):
                with open("config.py", "r", encoding="utf-8") as input_file:
                    content = input_file.read()
                print("config is ready for editing ...")
                print("To apply changes, save as 'config.py' and replace the existing 'config.py' when you finish editing.")
            self.cliTool(editor, content)
            config.saveConfigOnExit = False
            print(self.divider)
            print("Restarting ...")
            return ".restart"

    # pipe text content into a cli tool
    def cliTool(self, tool, content=""):
        if WebtopUtil.isPackageInstalled(tool):
            pydoc.pipepager(content, cmd=tool)
            if WebtopUtil.isPackageInstalled("pkill"):
                tool = tool.strip().split(" ")[0]
                os.system(f"pkill {tool}")
        else:
            self.printToolNotFound(tool)
        return ""

    def openNoteEditor(self, noteType, b=None, c=None, v=None, year=None, month=None, day=None, editor=None):
        if editor is None:
            editor = config.terminalNoteEditor
        if WebtopUtil.isPackageInstalled(editor.split(" ")[0]):
            noteDB = JournalSqlite() if noteType == "journal" else NoteSqlite()
            if noteType == "journal":
                note = noteDB.getJournalNote(year, month, day)
            elif noteType == "book":
                note = noteDB.getBookNote(b)[0]
            elif noteType == "chapter":
                note = noteDB.getChapterNote(b, c)[0]
            elif noteType == "verse":
                note = noteDB.getVerseNote(b, c, v)[0]
            if config.isMarkdownifyInstalled:
                # convert html into markdown
                from markdownify import markdownify
                note = markdownify(note, heading_style=config.markdownifyHeadingStyle)
                note = note.replace("\n\np, li { white-space: pre-wrap; }\n", "")
                note = note.replace("hr { height: 1px; border-width: 0; }\n", "")
            else:
                note = self.getPlainText(note)
            # display in editor
            print("Opening text editor ...")
            print("When you finish editing, save content in a file and enter 'note' as its filename.")
            self.cliTool(editor, note)
            # check if file is saved
            notePath = "note"
            if os.path.isfile(notePath):
                with open(notePath, "r", encoding="utf-8") as input_file:
                    text = input_file.read()
                # convert markdown into html
                text = markdown.markdown(text)
                text = TextUtil.fixNoteFontDisplay(text)
                #text = TextUtil.htmlWrapper(text, True, "study", False)
                # save into note databse
                self.saveNote(noteDB, noteType, b, c, v, year, month, day, text)
                # remove file after saving
                os.remove(notePath)
        else:
            self.printToolNotFound(editor)
            print("Install it first of run '.changenoteeditor' to change the default note editor.")
            return ""

    def saveNote(self, noteDB, noteType, b=None, c=None, v=None, year=None, month=None, day=None, note=""):
        note = TextUtil.fixNoteFont(note)
        if noteType == "book":
            #NoteService.saveBookNote(b, note)
            #noteDB = NoteSqlite()
            #noteDB.saveBookNote(b, note)
            noteDB.saveBookNote(b, note, DateUtil.epoch())
        elif noteType == "chapter":
            noteDB.saveChapterNote(b, c, note, DateUtil.epoch())
        elif noteType == "verse":
            noteDB.saveVerseNote(b, c, v, note, DateUtil.epoch())
        elif noteType == "journal":
            noteDB.saveJournalNote(year, month, day, note)
        print("Note saved!")

    # Toggle bible display

    def toggleBibleChapterFormat(self):
        config.readFormattedBibles = not config.readFormattedBibles
        print("Reloading bible chapter ...")
        return self.getContent(".l")

    def togglebiblecomparison(self):
        config.terminalBibleComparison = not config.terminalBibleComparison
        print("Reloading bible chapter ...")
        return self.getContent(".l")

    def toggleaddTitleToPlainChapter(self):
        config.addTitleToPlainChapter = not config.addTitleToPlainChapter
        print("Reloading bible chapter ...")
        return self.getContent(".l")

    def toggleaddFavouriteToMultiRef(self):
        config.addFavouriteToMultiRef = not config.addFavouriteToMultiRef
        print("Reloading bible chapter ...")
        return self.getContent(".l")

    def toggleshowVerseReference(self):
        config.showVerseReference = not config.showVerseReference
        print("Reloading bible chapter ...")
        return self.getContent(".l")

    def toggleshowUserNoteIndicator(self):
        config.showUserNoteIndicator = not config.showUserNoteIndicator
        print("Reloading bible chapter ...")
        return self.getContent(".l")

    def toggleshowBibleNoteIndicator(self):
        config.showBibleNoteIndicator = not config.showBibleNoteIndicator
        print("Reloading bible chapter ...")
        return self.getContent(".l")

    def togglehideLexicalEntryInBible(self):
        config.hideLexicalEntryInBible = not config.hideLexicalEntryInBible
        print("Reloading bible chapter ...")
        return self.getContent(".l")

    # organise user interactive menu

    def displayFeatureMenu(self, heading, features):
        featureItems = [f"[<ref>{index}</ref> {item if config.terminalDisplayCommandOnMenu else ''} ] {self.dotCommands[item][0]}" for index, item in enumerate(features)]
        content = f"<h2>{heading}</h2>"
        content += "<br>".join(featureItems)
        print(self.divider)
        print(TextUtil.htmlToPlainText(content).strip())
        print(self.divider)
        #self.printChooseItem()
        print("Enter a number:")
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            from util.PromptValidator import NumberValidator
            userInput = prompt(self.inputIndicator, style=self.promptStyle, validator=NumberValidator()).strip()
        else:
            userInput = input(self.inputIndicator).strip()
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        try:
            command = features[int(userInput)]
            self.printRunningCommand(command)
            return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def menu(self):
        heading = "UBA Terminal Mode Menu"
        features = [".show", ".open", ".search", ".note", ".edit", ".clipboard", ".quick", ".control", ".tools", ".plugins", ".change", ".download", ".maintain", ".develop", ".help", ".restart", ".quit"]
        if config.terminalMyMenu:
            features.insert(0, ".my")
        return self.displayFeatureMenu(heading, features)

    def my(self):
        if config.terminalMyMenu:
            heading = "My Menu"
            return self.displayFeatureMenu(heading, config.terminalMyMenu)
        else:
            return "Configure config.terminalMyMenu first!"

    def open(self):
        heading = "Open"
        features = (".openbible", ".openbiblenote", ".original", ".open365readingplan", ".openbookfeatures", ".openchapterfeatures", ".openversefeatures", ".opencommentary", ".openreferencebook", ".openaudio", ".opendata", ".opentopics", ".openpromises", ".openparallels", ".opennames", ".opencharacters", ".openlocations", ".openmaps", ".opentimelines", ".opendictionaries", ".openencyclopedia", ".openlexicons", ".openthirdpartydictionaries", ".opentext")
        return self.displayFeatureMenu(heading, features)

    def quick(self):
        heading = "Quick"
        features = (".quickopen", ".quickopencopiedtext", ".quickedit", ".quickeditcopiedtext", ".quicksearch", ".quicksearchcopiedtext")
        return self.displayFeatureMenu(heading, features)

    def original(self):
        heading = "Hebrew & Greek Bibles"
        features = (".mob", ".mib", ".mtb", ".mpb", ".mab", ".lxx1i", ".lxx2i")
        return self.displayFeatureMenu(heading, features)

    def tools(self):
        heading = "Tools"
        features = (".web", ".share", ".extract", ".filters", ".read", ".readsync", ".tts", ".googletranslate", ".watsontranslate")
        return self.displayFeatureMenu(heading, features)

    def control(self):
        heading = "Control"
        features = (".reload", ".latestbible", ".forward", ".backward", ".swap", ".starthttpserver", ".stophttpserver", ".stopaudio", ".stopaudiosync", ".toggle")
        return self.displayFeatureMenu(heading, features)

    def toggle(self):
        heading = "Toggle"
        features = (".togglepager", "toggleclipboardmonitor", ".togglebiblecomparison", ".togglebiblechapterplainlayout", ".toggleplainbiblechaptersubheadings", ".togglefavouriteverses", ".toggleversenumberdisplay", ".toggleusernoteindicator", ".togglebiblenoteindicator", ".togglebiblelexicalentries")
        return self.displayFeatureMenu(heading, features)

    def clipboard(self):
        heading = "Copy & Copied Text"
        features = (".copy", ".copyhtml", ".paste", ".run", ".findcopiedtext", ".ttscopiedtext", ".googletranslatecopiedtext", ".watsontranslatecopiedtext", ".extractcopiedtext")
        return self.displayFeatureMenu(heading, features)

    def search(self):
        heading = "Search"
        features = (".find", ".searchbible", ".searchpromises", ".searchparallels", ".searchnames", ".searchcharacters", ".searchlocations", ".searchtopics", ".searchreferencebooks", ".searchencyclopedia", ".searchdictionaries", ".searchthirdpartydictionaries", ".searchlexicons", ".searchlexiconsreversely", ".searchconcordance")
        return self.displayFeatureMenu(heading, features)

    def info(self):
        heading = "Information"
        features = (".latest", ".history", ".showbibles", ".showstrongbibles", ".showbiblebooks", ".showbibleabbreviations", ".showbiblechapters", ".showbibleverses", ".showcommentaries", ".showtopics", ".showlexicons", ".showencyclopedia", ".showdictionaries", ".showthirdpartydictionary", ".showreferencebooks", ".showdata", ".showttslanguages", ".commands", ".config")
        return self.displayFeatureMenu(heading, features)

    def edit(self):
        heading = "Edit"
        features = (".editnewfile", ".editcontent", ".editconfig", ".editfilters", ".changenoteeditor", ".helpinstallmicro")
        return self.displayFeatureMenu(heading, features)

    def change(self):
        heading = "Change"
        features = (".changecurrentbible", ".changefavouritebible1", ".changefavouritebible2", ".changefavouritebible3", ".changefavouriteoriginalbible", ".changecommentary", ".changelexicon", ".changedictionary", ".changethirdpartydictionary", ".changeencyclopedia", ".changeconcordance", ".changereferencebook", ".changettslanguage1", ".changettslanguage2", ".changettslanguage3", ".changedefaultcommand", ".changebiblesearchmode", ".changenoteeditor", ".changecolors", ".changeterminalmodeconfig", ".changeconfig")
        return self.displayFeatureMenu(heading, features)

    def help(self):
        heading = "Help"
        features = (".wiki", ".quickstart", ".howto", ".terminalcommands", ".standardcommands", ".aliases", ".whatis")
        return self.displayFeatureMenu(heading, features)

    def maintain(self):
        heading = "Maintenance"
        features = [".latestchanges", ".update"]
        if config.terminalEnableTermuxAPI:
            features += [".backup", ".restore"]
        return self.displayFeatureMenu(heading, features)

    def backup(self):
        heading = "Backup"
        features = (".backupnotes", ".backupjournals")
        return self.displayFeatureMenu(heading, features)

    def restore(self):
        heading = "Restore"
        features = (".restorenotes", ".restorelastnotes", ".restorejournals", ".restorelastjournals")
        return self.displayFeatureMenu(heading, features)

    def download(self):
        heading = "Download"
        features = (".showdownloads", ".downloadbibleaudio", ".downloadyoutube")
        return self.displayFeatureMenu(heading, features)

    def develop(self):
        heading = "Developers"
        features = (".gitstatus", ".exec", ".execfile", ".buildportablepython")
        return self.displayFeatureMenu(heading, features)

    def openbookfeatures(self):
        heading = "Bible Book Featues"
        features = (".openintroduction", ".opendictionarybookentry", ".openencyclopediabookentry")
        return self.displayFeatureMenu(heading, features)

    def openchapterfeatures(self):
        heading = "Bible Chapter Featues"
        features = (".openoverview", ".opensummary", ".openchapterindex")
        return self.displayFeatureMenu(heading, features)

    def openversefeatures(self):
        heading = "Bible Verse Featues"
        features = (".opencrossreference", ".opentske", ".opencomparison", ".opendifference", ".openverseindex", ".openwords", ".opendiscourse", ".opentranslation", ".opencombo")
        return self.displayFeatureMenu(heading, features)

    def accessNoteFeatures(self):
        heading = "Note / Journal Features"
        features = (".openbooknote", ".openchapternote", ".openversenote", ".openjournal", ".searchbooknote", ".searchchapternote", ".searchversenote", ".searchjournal", ".editbooknote", ".editchapternote", ".editversenote", ".editjournal", ".changenoteeditor")
        return self.displayFeatureMenu(heading, features)

    # Download Helper
    def downloadHelper(self, databaseInfo):
        if config.runMode == "terminal":
            if config.isDownloading:
                self.displayMessage(config.thisTranslation["previousDownloadIncomplete"])
            else:
                print(self.divider)
                print(f"Essential data '{databaseInfo[0][-1]}' is missing!")
                print("Do you want to download it now? [y]es / [N]o")
                userInput = self.simplePrompt()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput.lower() in ("y", "yes"):
                    self.textCommandParser.parent.downloadFile(databaseInfo)
                    return ""
                elif userInput.lower() in ("n", "no"):
                    return self.cancelAction()
                else:
                    self.printInvalidOptionEntered()

    def resizeHtmlImage(self, imageTag):
        return re.sub("^<img ", """<img style="max-width: 100%; height: auto;" """, imageTag)

    def saveAndOpenHtmlFile(self, html, filepath=""):
        if not filepath:
            filepath = os.path.join(os.getcwd(), "terminal_mode", "Unique_Bible_App.html")
        # write an html file
        with open(filepath, "w", encoding="utf-8") as fileObj:
            fileObj.write(html)
        # open the html file
        if config.terminalEnableTermuxAPI:
            print(f"Opening {filepath} ...")
            self.openLocalHtmlWithAndroidApps(filepath)
        else:
            command = f"cmd:::{config.open} {filepath}"
            self.printRunningCommand(command)
            self.getContent(command)

    def openLocalHtmlWithAndroidApps(self, filepath):
        if config.terminalEnableTermuxAPI:
            filepath = re.sub("/", r"%2F", filepath)
            filepath = re.sub(r"%2Fdata%2Fdata%2Fcom.termux%2Ffiles%2Fhome%2F", r"content://com.termux.documents/document/%2Fdata%2Fdata%2Fcom.termux%2Ffiles%2Fhome%2F", filepath)
            cmd = f"termux-open {filepath}"
            self.cliTool(cmd)

    def wrapHtml(self, content):
        return """
                <!DOCTYPE html><html><head><link rel="icon" href="icons/{2}"><title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />
                <style>
                table, th, td {0}
                border: 1px solid black;
                {1}
                </style>
                </head><body>
                {3}
                </body></html>
                """.format("{", "}", config.webUBAIcon, content)

    def wrapHtmlFull(self, content, view="", book=False):
        fontFamily = config.font
        fontSize = "{0}px".format(config.fontSize)
        if book:
            if config.overwriteBookFontFamily:
                fontFamily = config.overwriteBookFontFamily
            if config.overwriteBookFontSize:
                if type(config.overwriteBookFontSize) == str:
                    fontSize = config.overwriteBookFontSize
                elif type(config.overwriteBookFontSize) == int:
                    fontSize = "{0}px".format(config.overwriteBookFontSize)
        bcv = (config.studyText, config.studyB, config.studyC, config.studyV) if view == "study" else (config.mainText, config.mainB, config.mainC, config.mainV)
        activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(*bcv)
        html = ("""<!DOCTYPE html><html><head><link rel="icon" href="icons/{9}"><title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />"""
                "<style>body {2} font-size: {4}; font-family:'{5}';{3} "
                "zh {2} font-family:'{6}'; {3} "
                ".ubaButton {2} background-color: {10}; color: {11}; border: none; padding: 2px 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 17px; margin: 2px 2px; cursor: pointer; {3}"
                "{8}</style>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css?v=1.064'>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.064'>"
                "<script src='js/common.js?v=1.064'></script>"
                "<script src='js/{7}.js?v=1.064'></script>"
                "<script src='w3.js?v=1.064'></script>"
                "<script src='js/http_server.js?v=1.064'></script>"
                """<script>
                var target = document.querySelector('title');
                var observer = new MutationObserver(function(mutations) {2}
                    mutations.forEach(function(mutation) {2}
                        ubaCommandChanged(document.title);
                    {3});
                {3});
                var config = {2}
                    childList: true,
                {3};
                observer.observe(target, config);
                </script>"""
                "{0}"
                """<script>var versionList = []; var compareList = []; var parallelList = [];
                var diffList = []; var searchList = [];</script>"""
                "<script src='js/custom.js?v=1.064'></script>"
                "</head><body><span id='v0.0.0'></span>{1}"
                "<p>&nbsp;</p><div id='footer'><span id='lastElement'></span></div><script>loadBible();document.querySelector('body').addEventListener('click', window.parent.closeSideNav);</script></body></html>"
                ).format(activeBCVsettings,
                         content,
                         "{",
                         "}",
                         fontSize,
                         fontFamily,
                         config.fontChinese,
                         config.theme,
                         self.getHighlightCss(),
                         config.webUBAIcon,
                         config.widgetBackgroundColor,
                         config.widgetForegroundColor,
                         )
        return html

    def getHighlightCss(self):
        css = ""
        for i in range(len(config.highlightCollections)):
            code = "hl{0}".format(i + 1)
            css += ".{2} {0} background: {3}; {1} ".format("{", "}", code, config.highlightDarkThemeColours[i] if config.theme == "dark" else config.highlightLightThemeColours[i])
        return css

    # Workaround stoping audio playing in some cases
    def createAudioPlayingFile(self):
        # To break the audio playing loop running with readsync or Android tts, manually delete the file "temp/000_audio_playing.txt"
        if not os.path.isfile(config.audio_playing_file):
            open(config.audio_playing_file, "a", encoding="utf-8").close()

    def removeAudioPlayingFile(self):
        if os.path.isfile(config.audio_playing_file):
            os.remove(config.audio_playing_file)

    # Missing package
    def printMissingPackage(self, package):
        print(f"Essentail package '{package}' is not found!")
