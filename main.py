from analyzer.diff_parser import parse_diff
from analyzer.analyzer import analyze
from analyzer.ast_operator import collect_functiondef
import git
import os


def main():
    repo_path = os.path.join('REPO', 'pydantic')
    repo = git.Repo(repo_path)
    HEAD = repo.git.execute('git rev-parse HEAD')
    pre_HEAD = f'{HEAD}~1'
    diff_content = repo.git.diff(f'{pre_HEAD}~1', f'{pre_HEAD}')
    diff_infos = parse_diff(diff_content)
    for diff in diff_infos:
        # src_file_path = diff.src_file[2:]
        tar_file_path = diff.tar_file[2:]
        if tar_file_path.endswith('.py'):
            functiondef_list = collect_functiondef(os.path.join(repo_path, tar_file_path))
            print(diff)
            # print(functiondef_list)
    # results = collect_functiondef('REPO/pydantic/pydantic/json.py')
    # print(results)


if __name__ == '__main__':
    main()
