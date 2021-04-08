import logging
from github import Github
import config
import base64

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
        branch = self.repo.get_branch(self.repo.default_branch)
        sha = branch.commit.sha
        tree = self.repo.get_git_tree(sha)
        for element in tree.tree:
            print("{0}:{1}".format(element.path, element.sha))

    def downloadFile(self, dir, filename, sha):
        file = self.repo.get_git_blob(sha)
        decoded = base64.b64decode(file.content)
        with open(dir + "/" + filename, 'wb') as zipfile:
            zipfile.write(decoded)


if __name__ == "__main__":
    # github = GithubUtil("otseng/UniqueBible_Bibles")
    # github.printContentsOfRepo()

    github = GithubUtil("darrelwright/UniqueBible_Commentaries")
    github.printContentsOfRepo()
    github.downloadFile("output", "test.zip", "1274eccd33476b0e4716b41e292d50ad601715c8")

