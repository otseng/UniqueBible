import logging
import re
import time
import config

from github import Github, InputFileContent

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
from util.DateUtil import DateUtil


class GitHubGist:

    def __init__(self, gistToken=""):
        self.logger = logging.getLogger('uba')
        if not self.logger.hasHandlers():
            logHandler = logging.StreamHandler()
            logHandler.setLevel(logging.DEBUG)
            self.logger.addHandler(logHandler)
            self.logger.setLevel(logging.INFO)
        if gistToken == "":
            self.gistToken = config.gistToken
        else:
            self.gistToken = gistToken
        self.status = "Not configured"
        self.connected = False
        self.user = None
        self.gist = None
        self.description = None
        try:
            if len(self.gistToken) < 40:
                self.status = "Gist token is has valid"
                raise Exception(self.status)
            self.gh = Github(self.gistToken)
            self.user = self.gh.get_user()
            self.status = "Gist user: " + self.user.name
            self.logger.debug(self.status)
            self.connected = True
        except Exception as error:
            self.status = "Could not connect"
            self.logger.error(str(error))

    def open_gist_chapter_note(self, book, chapter):
        self.description = GitHubGist.bc_to_chapter_name(book, chapter)
        self.open_gist_by_description(self.description)

    def open_gist_verse_note(self, book, chapter, verse):
        self.description = GitHubGist.bc_to_verse_name(book, chapter, verse)
        self.open_gist_by_description(self.description)

    def open_gist_by_description(self, description):
        if self.user:
            self.gist = None
            gists = self.user.get_gists()
            for g in gists:
                if description == g.description:
                    self.gist = g
                    self.description = description
                    self.logger.debug("Existing Gist:{0}:{1}".format(description, self.gist.id))
                    break

    def open_gist_by_id(self, id):
        self.gist = None
        try:
            if self.gh:
                self.gist = self.gh.get_gist(id)
        except:
            return None
        if not self.description == self.gist.description:
            return None

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

    def update_content(self, content):
        if not self.gist:
            print("Creating gist {0}".format(self.description))
            self.gist = self.user.create_gist(False, {self.description: InputFileContent(content)}, self.description)
            self.logger.debug("New Gist :{0}:{1}".format(self.description, self.gist.id))
        else:
            print("Updating gist {0}".format(self.description))
            self.gist.edit(files={self.description: InputFileContent(content)})

    def get_file(self):
        if self.gist:
            files = self.gist.files
            file = files[self.description]
            return file
        else:
            return None

    def get_content(self):
        file = self.get_file()
        if file:
            return file.content
        else:
            return ""

    def get_updated(self):
        if self.gist:
            # doesn't work - last_modified is blank sometimes!
            # lm = self.gist.last_modified
            # return GitHubGist.extract_epoch(lm)
            updated = self.gist.updated_at
            return int(DateUtil.datetime_to_epoch(updated) - DateUtil.seconds_between_local_and_utc())
        else:
            return 0

    def delete_all_notes(self):
        if self.user:
            self.gist = None
            self.description = None
            gists = self.user.get_gists()
            for g in gists:
                if g.description.startswith("UBA-Note-"):
                    g.delete()

    def bc_to_chapter_name(b, c):
        return "UBA-Note-Chapter-{0}-{1}".format(b, c)

    def bc_to_verse_name(b, c, v):
        return "UBA-Note-Verse-{0}-{1}-{2}".format(b, c, v)

    def chapter_name_to_bc(name):
        res = re.search(r'UBA-Note-Chapter-(\d*)-(\d*)', name).groups()
        return res

    def verse_name_to_bc(name):
        res = re.search(r'UBA-Note-Verse-(\d*)-(\d*)-(\d*)', name).groups()
        return res

    def extract_content(gist):
        return gist.files[gist.description].content

    def extract_epoch(datetime):
        if datetime:
            st = time.strptime(datetime, "%a, %d %b %Y %H:%M:%S GMT")
            return int(time.mktime(st))
        else:
            return 0

#
# Only used for testing
#

def test_write():
    gh = GitHubGist()
    if not gh.connected:
        print(gh.status)
    else:
        book = 40
        chapter = 1
        gh.open_gist_chapter_note(book, chapter)
        gh.update_content("Matthew chapter change from command line")
        updated = gh.get_updated()
        print(updated)
        file = gh.get_file()
        if file:
            print(file.content)
            print(gh.id())
        else:
            print(gh.description + " gist does not exist")
            print(gh.id())

        print("---")

        book = 40
        chapter = 1
        verse = 2
        gh.open_gist_verse_note(book, chapter, verse)
        gh.update_content("Matthew verse 2 from command line")
        file = gh.get_file()
        updated = gh.get_updated()
        print(updated)
        if file:
            print(gh.id())
            print(file.content)
        else:
            print(gh.description + " gist does not exist")

def test_read():
    gh = GitHubGist()
    if not gh.connected:
        print(gh.status)
    else:
        book = 40
        chapter = 1
        gh.open_gist_chapter_note(book, chapter)
        updated = gh.get_updated()
        print(updated)
        file = gh.get_file()
        if file:
            print(file.content)
            print(gh.id())
        else:
            print(gh.description + " gist does not exist")
            print(gh.id())

        print("---")

        book = 40
        chapter = 1
        verse = 2
        gh.open_gist_verse_note(book, chapter, verse)
        file = gh.get_file()
        updated = gh.get_updated()
        print(updated)
        if file:
            print(gh.id())
            print(file.content)
        else:
            print(gh.description + " gist does not exist")

def test_names():
    chapter = "UBA-Note-Chapter-1-2"
    res = GitHubGist.chapter_name_to_bc(chapter)
    print(res)
    verse = "UBA-Note-Verse-10-4-5"
    res = GitHubGist.verse_name_to_bc(verse)
    print(res)

def test_get_notes():
    gh = GitHubGist()
    notes = gh.get_all_note_gists()
    for gist in notes:
        print(gist.id)
        print(gist.description)
        content = GitHubGist.extract_content(gist)
        modified = GitHubGist.extract_epoch(gist.last_modified)
        print(modified)
        # print(content)

def test_updated():
    gh = GitHubGist()
    book = 40
    chapter = 1
    gh.open_gist_chapter_note(book, chapter)
    updated = gh.get_updated()
    print(updated)
    content = gh.get_content()
    print(content)

def test_time():
    struct = time.strptime("Wed, 03 Feb 2021 03:44:38 GMT", "%a, %d %b %Y %H:%M:%S GMT")
    print(time.mktime(struct))
    print(time.mktime(time.gmtime()))

def test_delete():
    gh = GitHubGist()
    gh.delete_all_notes()

if __name__ == "__main__":
    start = time.time()

    test_delete()

    print("---")

    end = time.time()
    print("Epoch: {0}".format(DateUtil.epoch()))
    print("Total time: {0}".format(end - start))
