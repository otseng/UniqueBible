import logging
import sys
from logging import handlers

from github import Github, InputFileContent
import config

# https://docs.github.com/en/rest/reference/gists
# https://pygithub.readthedocs.io/en/latest/introduction.html
# https://pygithub.readthedocs.io/en/latest/reference.html

class GitHubGist:

    def __init__(self, name):
        self.logger = logging.getLogger('uba')
        if not self.logger.hasHandlers():
            logHandler = logging.StreamHandler()
            logHandler.setLevel(logging.DEBUG)
            self.logger.addHandler(logHandler)
            self.logger.setLevel(logging.DEBUG)
        self.gist = None
        self.connected = False
        self.status = "Not configured"
        try:
            if len(config.gistToken) == 0:
                self.status = "gistToken has not been set in config"
                raise Exception(self.status)
            self.gh = Github(config.gistToken)
            self.user = self.gh.get_user()
            self.name = name
            self.status = "Gist user: " + self.user.name
            self.logger.info(self.status)
            self.connected = True
            gists = self.user.get_gists()
            for g in gists:
                if self.name == g.description:
                    self.gist = g
                    self.logger.debug("Found Gist " + self.name)
                    break
            if not self.gist:
                self.logger.debug("Creating Gist " + self.name)
                self.gist = self.user.create_gist(False, {self.name: InputFileContent(self.name)}, self.name)
        except Exception as error:
            self.status = error
            self.logger.error(self.status)

    def update_gist(self, file, contents):
        if self.gist:
            self.gist.edit(files={file: contents})

    def get_files(self):
        if self.gist:
            return self.gist.files

if __name__ == "__main__":

    ghGist = GitHubGist("UBA Notes")
    if not ghGist.connected:
        print(ghGist.status)
    else:
        ghGist.update_gist("Chapter-1-1", InputFileContent("In the beginning"))
        ghGist.update_gist("Verse-40-1-1", InputFileContent("First book of NT"))
        files = ghGist.get_files()
        if files:
            for filename in files:
                print(filename)
