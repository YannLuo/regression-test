import os
import git


class GitOperator(object):
    def __init__(self, repo_dir):
        self.repo_dir = repo_dir
        self.repo = git.Repo(self.repo_dir)

    def get_git_diff_content(self, sha):
        return self.repo.git.diff(f'{sha}~1', sha)

    def change_sha(self, sha):
        self.repo.git.checkout(sha)
