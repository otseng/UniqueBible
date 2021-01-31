from github import Github, InputFileContent
import config


class GitHubGist:

    def __init__(self, name):
        self.name = name
        self.gh = Github(config.gistToken)
        self.user = self.gh.get_user()
        print("Logged in as " + self.user.name)
        gists = self.user.get_gists()
        self.gist = None
        for g in gists:
            if self.name == g.description:
                self.gist = g
                print("Found " + self.name)
                break
        if not self.gist:
            print("Creating " + self.name)
            self.gist = self.user.create_gist(False, {self.name: InputFileContent(self.name)}, self.name)

    def update_gist(self, file, contents):
        self.gist.edit(files={file: contents})
        print("Updating")

if __name__ == "__main__":

    githubGist = GitHubGist("UBA Notes")
    githubGist.update_gist("Chapter-1-1", InputFileContent("In the beginning"))
    githubGist.update_gist("Verse-40-1-1", InputFileContent("First book of NT"))
