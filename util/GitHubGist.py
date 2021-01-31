import logging
import sys
from logging import handlers

from github import Github, InputFileContent
import config

# https://docs.github.com/en/rest/reference/gists
# https://pygithub.readthedocs.io/en/latest/introduction.html
# https://pygithub.readthedocs.io/en/latest/reference.html

class GitHubGist:

    def __init__(self):
        self.logger = logging.getLogger('uba')
        if not self.logger.hasHandlers():
            logHandler = logging.StreamHandler()
            logHandler.setLevel(logging.DEBUG)
            self.logger.addHandler(logHandler)
            self.logger.setLevel(logging.DEBUG)
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
            self.logger.info(self.status)
            self.connected = True
        except Exception as error:
            self.status = error
            self.logger.error(self.status)

    def open_gist_chapter_note(self, book, chapter):
        name = self.chapter_name(book, chapter)
        self.name = name
        self.open_gist_by_description(self.name)

    def open_gist_verse_note(self, book, chapter, verse):
        name = self.verse_name(book, chapter, verse)
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
                    self.description = description
                    self.logger.debug("Existing Gist :{0}:{1}".format(description, self.gist.id))
                    break
            if not self.gist:
                self.gist = self.user.create_gist(False, {self.name: InputFileContent("&nbsp;")}, self.name)
                self.description = description
                self.logger.debug("New Gist :{0}:{1}".format(description, self.gist.id))

    def update_file(self, content):
        if self.gist:
            self.gist.edit(files={self.name: content})

    def get_file(self):
        if self.gist:
            files = self.gist.files
            file = files[self.name]
            return file

    def chapter_name(self, b, c):
        return "UBA-Note-Chapter-{0}-{1}".format(b, c)

    def verse_name(self, b, c, v):
        return "UBA-Note-Verse-{0}-{1}-{2}".format(b, c, v)

if __name__ == "__main__":

    ghGist = GitHubGist()
    if not ghGist.connected:
        print(ghGist.status)
    else:
        book = 1
        chapter = 1
        ghGist.open_gist_chapter_note(book, chapter)
        # ghGist.update_file(InputFileContent("In the beginning, God created the heavens"))
        # file = ghGist.get_file()
        # print(file.content)

        book = 40
        chapter = 1
        verse = 1
        ghGist.open_gist_verse_note(book, chapter, verse)
        # file = ghGist.get_file()
        # print(file.content)
        # print(ghGist.gist.id)
