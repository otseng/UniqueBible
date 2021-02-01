from NoteSqlite import NoteSqlite
from util.GitHubGist import GitHubGist


class NoteService:

    ns = None

    def getNoteSqlite():
        if not NoteService.ns:
            NoteService.ns = NoteSqlite()
        return NoteService.ns

    def getChapterNote(b, c):
        ns = NoteService.getNoteSqlite()
        note, updated = ns.displayChapterNote(b, c)
        return note

    def saveChapterNote(b, c, note):
        ghGist = GitHubGist()
        ghGist.open_gist_chapter_note(b, c)
        ghGist.update_file(note)
        ns = NoteService.getNoteSqlite()
        ns.saveChapterNote(b, c, note)

    def getVerseNote(b, c, v):
        ns = NoteService.getNoteSqlite()
        note, updated = ns.displayVerseNote(b, c, v)
        return note

    def saveVerseNote(b, c, v, note):
        ghGist = GitHubGist()
        ghGist.open_gist_verse_note(b, c, v)
        ghGist.update_file(note)
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
