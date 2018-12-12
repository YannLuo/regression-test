from analyzer.diff_parser import parse_diff
from analyzer.ast_operator import collect_functiondef
import git
import os
from logger import create_logger
import time
from analyzer.callgraph.callgraph import dump_callgraph
import json
from collections import defaultdict


def main():
    # ========== generate callgraph ==========

    # logger = create_logger('log.log')
    #
    # repo_path = os.path.join('ecosystem', '**', '*.py')
    # stt = time.clock()
    # graph = dump_callgraph(repo_path, logger=logger)
    # edt = time.clock()
    # print("Generate callgraph cost %.2f minutes." % ((edt - stt) / 60.0, ))

    # ========== analyze git diff and dump modified function/method ==========

    repo_path = os.path.join('REPOS', 'numpy')
    repo = git.Repo(repo_path)
    commit_sha = "5e6ff3f"
    pre_commit_sha = f"{commit_sha}~5"
    diff_content = repo.git.diff(pre_commit_sha, commit_sha)
    diff_infos = parse_diff(diff_content)

    mod_functiondef_list = set()

    for diff in diff_infos:

        repo.git.checkout(commit_sha)
        tar_file_path = diff.tar_file[2:]
        if tar_file_path.endswith('.py'):
            tar_module = '.'.join(tar_file_path[:-3].split('/'))
            functiondef_list = collect_functiondef(os.path.join(repo_path, tar_file_path))
            for add_lineno in diff.hunk_infos["a"]:
                for i in range(len(functiondef_list)-1):
                    if functiondef_list[i].start_lineno <= add_lineno < functiondef_list[i+1].start_lineno:
                        mod_functiondef_list.add((tar_module, functiondef_list[i].name))
        repo.git.checkout(['-f', 'master'])

        repo.git.checkout(pre_commit_sha)
        src_file_path = diff.src_file[2:]
        if src_file_path.endswith('.py'):
            src_module = '.'.join(src_file_path[:-3].split('/'))
            functiondef_list = collect_functiondef(os.path.join(repo_path, src_file_path))
            for del_lineno in diff.hunk_infos["d"]:
                for i in range(len(functiondef_list) - 1):
                    if functiondef_list[i].start_lineno <= del_lineno < functiondef_list[i + 1].start_lineno:
                        mod_functiondef_list.add((src_module, functiondef_list[i].name))
        repo.git.checkout(['-f', 'master'])

    # ========== calculate reverse callgraph ==========

    with open("callgraph.json", mode='r', encoding='utf-8') as rf:
        callgraph = json.load(rf)

    rev_callgraph = defaultdict(set)
    for caller, callee_list in callgraph.items():
        for callee in callee_list:
            rev_callgraph["%s %s" % (callee["namespace"], callee["name"])].add(caller)

    # ========== analyze change impact ==========

    selected_tests_module = set()
    for prefix_namespace, name in mod_functiondef_list:
        q = []
        s = set()
        for cur_call in rev_callgraph:
            if cur_call.startswith(prefix_namespace):
                for si in rev_callgraph[cur_call]:
                    if si not in s:
                        q.append(si)
                        s.add(si)
        while len(q):
            top = q[0]
            q = q[1:]
            if top in rev_callgraph:
                for si in rev_callgraph[top]:
                    if si not in s:
                        q.append(si)
                        s.add(si)

        for si in s:
            if ".tests." in si:
                selected_tests_module.add(si.split(' ')[0])

    for item in selected_tests_module:
        print(item)


if __name__ == '__main__':
    main()
