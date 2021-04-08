import logging
from github import Github
import config


class GithubUtil:

    def __init__(self, repo=""):
        self.logger = logging.getLogger('uba')
        accessToken = config.githubAccessToken
        self.repo = None
        self.g = Github(accessToken)
        if len(repo) > 0:
            self.repo = self.g.get_repo(repo)

    def printAllPersonalRepos(self):
        if self.repo:
            for repo in self.g.get_user().get_repos():
                print(repo.name)

    def printBranches(self):
        branches = self.repo.get_branches()
        for branch in branches:
            print(branch)

    def printContentsOfRepo(self):
        contents = self.repo.get_contents("")
        for contentFile in contents:
            print(contentFile.name)


if __name__ == "__main__":
    # github = GithubUtil("otseng/UniqueBible_Bibles")
    # github.printContentsOfRepo()

    github = GithubUtil("darrelwright/UniqueBible_Commentaries")
    github.printContentsOfRepo()

