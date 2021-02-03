import logging
import re
import time

from github import Github, InputFileContent
import config

# https://docs.github.com/en/rest/reference/gists
# https://pygithub.readthedocs.io/en/latest/introduction.html
# https://pygithub.readthedocs.io/en/latest/reference.html

# gist object
#   comments (int)
#   description (str)
#   files (dict)
#   id (str)
#   last_modified (str)
#   public (bool)
#   updated_at (datetime)

class GitHubGist:

    def __init__(self):
        self.logger = logging.getLogger('uba')
        if not self.logger.hasHandlers():
            logHandler = logging.StreamHandler()
            logHandler.setLevel(logging.DEBUG)
            self.logger.addHandler(logHandler)
            self.logger.setLevel(logging.INFO)
        self.status = "Not configured"
        self.connected = False
        self.user = None
        self.gist = None
        self.description = None
        self.name = None
        try:
            if len(config.gistToken) == 0:
                self.status = "gistToken has not been set in config"
                raise Exception(self.status)
            self.gh = Github(config.gistToken)
            self.user = self.gh.get_user()
            self.status = "Gist user: " + self.user.name
            self.logger.debug(self.status)
            self.connected = True
        except Exception as error:
            self.status = error
            self.logger.error(self.status)

    def open_gist_chapter_note(self, book, chapter):
        name = GitHubGist.chapter_name(book, chapter)
        self.name = name
        self.open_gist_by_description(self.name)

    def open_gist_verse_note(self, book, chapter, verse):
        name = GitHubGist.verse_name(book, chapter, verse)
        self.name = name
        self.open_gist_by_description(self.name)

    def open_gist_by_description(self, description):
        if self.user:
            self.gist = None
            self.description = None
            gists = self.user.get_gists()
            for g in gists:
                if description == g.description:
                    self.gist = g
                    self.name = description
                    self.logger.debug("Existing Gist:{0}:{1}".format(description, self.gist.id))
                    break

    def open_gist_by_id(self, id):
        if self.gh:
            self.gist = self.gh.get_gist(id)
            self.name = self.gist.description

    def get_all_note_gists(self):
        if self.user:
            self.gist = None
            self.description = None
            gists = self.user.get_gists()
            notes = []
            for g in gists:
                if g.description.startswith("UBA-Note-"):
                    notes.append(g)
            return notes

    def id(self):
        if self.gist:
            return self.gist.id
        else:
            return ""

    def name(self):
        if self.gist:
            return self.gist.description
        else:
            return ""

    def update_content(self, content):
        if not self.gist:
            self.gist = self.user.create_gist(False, {self.name: InputFileContent(content)}, self.name)
            self.logger.debug("New Gist :{0}:{1}".format(self.name, self.gist.id))
        else:
            self.gist.edit(files={self.name: InputFileContent(content)})

    def get_file(self):
        if self.gist:
            files = self.gist.files
            file = files[self.name]
            return file
        else:
            return None

    def get_content(self):
        file = self.get_file()
        if file:
            return file.content
        else:
            return ""

    def get_last_modified(self):
        if self.gist:
            return self.gist.last_modified

    def chapter_name(b, c):
        return "UBA-Note-Chapter-{0}-{1}".format(b, c)

    def verse_name(b, c, v):
        return "UBA-Note-Verse-{0}-{1}-{2}".format(b, c, v)

    def extract_bc(name):
        res = re.search(r'UBA-Note-Chapter-(\d*)-(\d*)', name).groups()
        return res

    def extract_bcv(name):
        res = re.search(r'UBA-Note-Verse-(\d*)-(\d*)-(\d*)', name).groups()
        return res

    def extract_content(gist):
        return gist.files[gist.description].content

def test1():
    gh = GitHubGist()
    if not gh.connected:
        print(gh.status)
    else:
        book = 40
        chapter = 1
        gh.open_gist_chapter_note(book, chapter)
        gh.update_content("Matthew chapter change from command line")
        file = gh.get_file()
        updated = gh.get_last_modified()
        print(updated)
        if file:
            print(file.content)
            print(gh.id())
        else:
            print(gh.name + " gist does not exist")
            print(gh.id())

        print("---")

        book = 40
        chapter = 1
        verse = 2
        gh.open_gist_verse_note(book, chapter, verse)
        gh.update_content("Matthew verse 2 from command line")
        print(gh.get_last_modified())
        # Wed, 03 Feb 2021 03:44:38 GMT
        file = gh.get_file()
        if file:
            print(gh.id())
            print(file.content)
        else:
            print(gh.name + " gist does not exist")

        print("---")

def test2():
    chapter = "UBA-Note-Chapter-1-2"
    res = GitHubGist.extract_bc(chapter)
    print(res)
    verse = "UBA-Note-Verse-10-4-5"
    res = GitHubGist.extract_bcv(verse)
    print(res)

def test3():
    gh = GitHubGist()
    gh.open_gist_by_id("9a5331cc774aeb361780f90e0492461a")
    content = gh.get_content()
    print(content)

def test4():
    gh = GitHubGist()
    notes = gh.get_all_note_gists()
    for gist in notes:
        print(gist.description)
        content = GitHubGist.extract_content(gist)
        print(content)

def test5():
    struct = time.strptime("Wed, 03 Feb 2021 03:44:38 GMT", "%a, %d %b %Y %H:%M:%S %Z")
    print(time.mktime(struct))
    print(int(time.time()))

if __name__ == "__main__":

    test5()
