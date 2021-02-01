import logging
import time

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
                    self.logger.debug("Existing Gist:{0}:{1}".format(description, self.gist.id))
                    break

    def open_gist_by_id(self, id):
        if self.user:
            self.gist = self.user.get_gist(id)

    def update_file(self, content):
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

    def chapter_name(self, b, c):
        return "UBA-Note-Chapter-{0}-{1}".format(b, c)

    def verse_name(self, b, c, v):
        return "UBA-Note-Verse-{0}-{1}-{2}".format(b, c, v)

    def get_updated(self):
        if self.gist:
            return int(self.gist.updated_at.timestamp())

if __name__ == "__main__":

    ghGist = GitHubGist()
    if not ghGist.connected:
        print(ghGist.status)
    else:
        book = 40
        chapter = 1
        ghGist.open_gist_chapter_note(book, chapter)
        ghGist.update_file("Matthew chapter change from command line")
        file = ghGist.get_file()
        updated = ghGist.get_updated()
        print(updated)
        if file:
            print(file.content)
        else:
            print(ghGist.name + " gist does not exist")

        print("---")

        book = 40
        chapter = 1
        verse = 2
        ghGist.open_gist_verse_note(book, chapter, verse)
        ghGist.update_file("Matthew verse 2 from command line")
        print(ghGist.get_updated())
        file = ghGist.get_file()
        if file:
            print(ghGist.gist.id)
            print(file.content)
        else:
            print(ghGist.name + " gist does not exist")

        print("---")

        print(int(time.time()))
