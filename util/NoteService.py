import time

from PySide2.QtWidgets import QApplication

import config
from Languages import Languages
from NoteSqlite import NoteSqlite
from util.GitHubGist import GitHubGist


class NoteService:

    ns = None

    def getNoteSqlite():
        if not NoteService.ns:
            NoteService.ns = NoteSqlite()
        return NoteService.ns

    def getChapterNote(b, c):
        validGist = False
        if config.enableGist:
            gh = GitHubGist()
            gh.open_gist_chapter_note(b, c)
            file = gh.get_file()
            updatedG = gh.get_updated()
            if file:
                noteG = file.content
                validGist = True
        ns = NoteService.getNoteSqlite()
        noteL, updatedL = ns.displayChapterNote(b, c)
        validLocal = True
        if noteL == config.thisTranslation["empty"]:
            validLocal = False
        if validGist and not validLocal:
            ns.saveChapterNote(b, c, noteG)
            note = noteG
        elif not validGist and validLocal:
            if config.enableGist:
                gh.update_content(noteL)
            note = noteL
        elif validGist and validLocal:
            if updatedL is None or updatedG > updatedL:
                note = noteG
            else:
                note = noteL
        else:
            note = noteL
        return note

    def saveChapterNote(b, c, note):
        gistId = None
        if config.enableGist:
            gh = GitHubGist()
            gh.open_gist_chapter_note(b, c)
            gh.update_content(note)
            gistId = gh.id()
        ns = NoteService.getNoteSqlite()
        ns.saveChapterNote(b, c, note)

    def getVerseNote(b, c, v):
        validGist = False
        if config.enableGist:
            gh = GitHubGist()
            gh.open_gist_verse_note(b, c, v)
            file = gh.get_file()
            updatedG = gh.get_updated()
            if file:
                noteG = file.content
                validGist = True
        ns = NoteService.getNoteSqlite()
        noteL, updatedL = ns.displayVerseNote(b, c, v)
        validLocal = True
        if noteL == config.thisTranslation["empty"]:
            validLocal = False
        if validGist and not validLocal:
            ns.saveVerseNote(b, c, noteG)
            note = noteG
        elif not validGist and validLocal:
            if config.enableGist:
                gh.update_content(noteL)
            note = noteL
        elif validGist and validLocal:
            if updatedL is None or updatedG > updatedL:
                note = noteG
            else:
                note = noteL
        else:
            note = noteL
        return note

    def saveVerseNote(b, c, v, note):
        if config.enableGist:
            gh = GitHubGist()
            gh.open_gist_verse_note(b, c, v)
            gh.update_content(note)
        ns = NoteService.getNoteSqlite()
        ns.saveVerseNote(b, c, v, note)

    def getSearchedChapterList(command):
        ns = NoteService.getNoteSqlite()
        chapters = ns.getSearchedChapterList(command)
        return chapters

    def getSearchedVerseList(command):
        ns = NoteService.getNoteSqlite()
        verses = ns.getSearchedVerseList(command)
        return verses

    def getChapterVerseList(b, c):
        ns = NoteService.getNoteSqlite()
        noteVerseList = ns.getChapterVerseList(b, c)
        return noteVerseList

    def isChapterNote(b, c):
        ns = NoteService.getNoteSqlite()
        result = ns.isChapterNote(b, c)
        return result

    def uploadToGist(parent):
        gh = GitHubGist()
        ns = NoteService.getNoteSqlite()
        count = 0
        notes = ns.getAllChapters() + ns.getAllVerses()
        for note in notes:
            count += 1
            book = note[0]
            chapter = note[1]
            verse = note[2]
            content = note[3]
            updatedL = note[4]
            if verse == 0:
                gh.open_gist_chapter_note(book, chapter)
            else:
                gh.open_gist_verse_note(book, chapter, verse)
            if parent and "setStatus" in dir(parent):
                if count % 10 == 0:
                    parent.setStatus("Uploading " + gh.description + " ...", True)
                    QApplication.processEvents()
            updatedG = gh.get_updated()
            if updatedG == 0:
                gh.update_content(content)
            elif updatedL is not None and updatedL > updatedG:
                gh.update_content(content)
            else:
                gistFile = gh.get_file()
                sizeG = gistFile.size
                sizeL = len(content)
                if sizeL > sizeG:
                    gh.update_content(content)
        return count

def test_note():
    b = 40
    c = 1

    note = NoteService.getChapterNote(b, c)
    print(note)

    gh = GitHubGist()
    gh.open_gist_chapter_note(b, c)
    print(gh.get_updated())

def test_get_all_notes():
    ns = NoteService.getNoteSqlite()
    notes = ns.getAllChapters() + ns.getAllVerses()
    return notes

if __name__ == "__main__":
    config.thisTranslation = Languages.translation
    start = time.time()

    test_get_all_notes()

    print("---")
    end = time.time()
    print("Total time: {0}".format(end - start))

