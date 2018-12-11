from analyzer.diff_parser import parse_diff
from analyzer.ast_operator import collect_functiondef
import git
import os
import json
from logger import create_logger
import time
from analyzer.callgraph.callgraph import dump_callgraph
from collections import defaultdict


def save_callgraph_to_json(graph):
    new_graph = defaultdict(list)
    for k, v in graph.items():
        for vi in v:
            namespace = '.'.join(vi.namespace.split(".")[1:])
            vi.namespace = namespace
        caller = '.'.join(k.split(".")[1:])
        new_graph[caller] = v

    with open('callgraph.json', mode='w', encoding='utf-8') as wf:
        wf.write(
            json.dumps(new_graph,
                       default=lambda o: {
                           "namespace": o.__dict__["namespace"],
                           "name": o.__dict__["name"],
                           "flavor": o.__dict__["flavor"]
                       },
                       indent=4)
        )
    return new_graph


def main():
    # ========== generate callgraph ==========

    # logger = create_logger('log.log')
    #
    # repo_path = os.path.join('ecosystem', '**', '*.py')
    # stt = time.clock()
    # graph = dump_callgraph(repo_path, logger=logger)
    # edt = time.clock()
    # print("Generate callgraph cost %.2f minutes." % ((edt - stt) / 60.0,))
    #
    # save_callgraph_to_json(graph)

    # ========== analyze git diff ==========

    repo_path = os.path.join('REPOS', 'numpy')
    repo = git.Repo(repo_path)
    commit_sha = "0f59087af94b4fba61138334bf8f9c375bf1ae55"
    pre_commit_sha = f"{commit_sha}~1"
    diff_content = repo.git.diff(pre_commit_sha, commit_sha)
    diff_infos = parse_diff(diff_content)

    mod_functiondef = set()

    for diff in diff_infos:
        tar_file_path = diff.tar_file[2:]
        repo.git.checkout(commit_sha)
        if tar_file_path.endswith('.py'):
            tar_module = '.'.join(tar_file_path[:-3].split('/'))
            functiondef_list = collect_functiondef(os.path.join(repo_path, tar_file_path))
            for add_lineno in diff.hunk_infos["a"]:
                for i in range(len(functiondef_list)-1):
                    if functiondef_list[i].start_lineno <= add_lineno < functiondef_list[i+1].start_lineno:
                        mod_functiondef.add((tar_module, functiondef_list[i].name))

        src_file_path = diff.src_file[2:]
        repo.git.checkout(pre_commit_sha)
        if src_file_path.endswith('.py'):
            src_module = '.'.join(src_file_path[:-3].split('/'))
            functiondef_list = collect_functiondef(os.path.join(repo_path, src_file_path))
            for del_lineno in diff.hunk_infos["d"]:
                for i in range(len(functiondef_list) - 1):
                    if functiondef_list[i].start_lineno <= del_lineno < functiondef_list[i + 1].start_lineno:
                        mod_functiondef.add((src_module, functiondef_list[i].name))

    repo.git.checkout('master')

    print(mod_functiondef)


if __name__ == '__main__':
    main()
