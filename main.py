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
    # callgraph = dump_callgraph(repo_path, logger=logger)
    # edt = time.clock()
    # print("Generate callgraph cost %.2f minutes." % ((edt - stt) / 60.0, ))

    # ========== analyze git diff and dump modified function/method ==========

    repo_path = os.path.join('REPOS', 'numpy')
    repo = git.Repo(repo_path)
    commit_sha = "7a3c50a"
    pre_commit_sha = f"{commit_sha}~1"
    diff_content = repo.git.diff(pre_commit_sha, commit_sha)
    diff_infos = parse_diff(diff_content)

    mod_functiondef_list = set()

    for diff in diff_infos:
        try:
            repo.git.checkout(['-f', commit_sha])
        except:
            pass
        tar_file_path = diff.tar_file[2:]
        if tar_file_path.endswith('.py'):
            tar_module = '.'.join(tar_file_path[:-3].split('/'))
            functiondef_list = collect_functiondef(os.path.join(repo_path, tar_file_path))
            for add_lineno in diff.hunk_infos["a"]:
                for i in range(len(functiondef_list)-1):
                    if functiondef_list[i].start_lineno <= add_lineno < functiondef_list[i+1].start_lineno:
                        mod_functiondef_list.add((tar_module, functiondef_list[i].name))
        try:
            repo.git.checkout(['-f', 'master'])
        except:
            pass

        try:
            repo.git.checkout(['-f', pre_commit_sha])
        except:
            pass
        src_file_path = diff.src_file[2:]
        if src_file_path.endswith('.py'):
            src_module = '.'.join(src_file_path[:-3].split('/'))
            functiondef_list = collect_functiondef(os.path.join(repo_path, src_file_path))
            for del_lineno in diff.hunk_infos["d"]:
                for i in range(len(functiondef_list) - 1):
                    if functiondef_list[i].start_lineno <= del_lineno < functiondef_list[i + 1].start_lineno:
                        mod_functiondef_list.add((src_module, functiondef_list[i].name))
        try:
            repo.git.checkout(['-f', 'master'])
        except:
            pass

    # ========== calculate reverse callgraph ==========

    # with open("callgraph.json", mode='r', encoding='utf-8') as rf:
    #     callgraph = json.load(rf)

    callgraph = defaultdict(set)
    with open("astropy_callgraph.txt", mode="r", encoding="utf-8") as rf:
        lines = rf.readlines()
    for line in lines:
        src, dst = line.strip().split()
        # if (src.startswith("numpy") or src.startswith("astropy")) and (dst.startswith("numpy") or dst.startswith("astropy")):
        if (src.startswith("numpy") and dst.startswith("numpy")) or \
                (src.startswith("astropy") and any([dst.startswith(x) for x in ("numpy", "astropy")])):
            callgraph[src].add(dst)

    test_files = set()
    for caller, callees in callgraph.items():
        if ".tests." in caller and caller.startswith('astropy'):
            spl_file = []
            spl_cs = caller.split('.')[:-1]
            for ssi in spl_cs:
                if ssi[0].isupper():
                    break
                spl_file.append(ssi)
            file = '.'.join(spl_file)
            test_files.add(file)
        for callee in callees:
            if ".tests." in callee and callee.startswith('astropy'):
                spl_file = []
                spl_cs = callee.split('.')[:-1]
                for ssi in spl_cs:
                    if ssi[0].isupper():
                        break
                    spl_file.append(ssi)
                file = '.'.join(spl_file)
                test_files.add(file)
    print(len(test_files))

    rev_callgraph = defaultdict(set)
    for caller, callee_list in callgraph.items():
        for callee in callee_list:
            rev_callgraph[callee].add(caller)

    for k in rev_callgraph:
        rev_callgraph[k] = list(rev_callgraph[k])

    with open('rev_callgraph.json', mode='w', encoding='utf-8') as wf:
        wf.write(
            json.dumps(rev_callgraph,
                       default=lambda o: o.__dict__,
                       indent=4)
        )

    # ========== analyze change impact ==========

    with open('rev_callgraph.json', mode='r', encoding='utf-8') as rf:
        rev_callgraph = json.load(rf)

    s = set()
    q = []
    for prefix_namespace, name in mod_functiondef_list:
        for cur_call in rev_callgraph:
            if cur_call.startswith(prefix_namespace) and cur_call.split('.')[-1] == name and cur_call not in s:
                if cur_call not in s:
                    q.append(cur_call)
                    s.add(cur_call)

    # q = ['numpy.ma.extras._median']
    # print(q)

    while len(q):
        top = q[0]
        # print(top)
        spl_file = []
        spl_si = top.split('.')[:-1]
        for ssi in spl_si:
            if ssi[0].isupper():
                break
            spl_file.append(ssi)
        q = q[1:]
        if top in rev_callgraph:
            for si in rev_callgraph[top]:
                if si not in s:
                    q.append(si)
                    s.add(si)
                    spl_file = []
                    spl_si = si.split('.')[:-1]
                    for ssi in spl_si:
                        if ssi[0].isupper():
                            break
                        spl_file.append(ssi)

    selected_tests_module = set()
    for si in s:
        if ".tests." in si and si.startswith('astropy'):
            spl_file = []
            spl_si = si.split('.')[:-1]
            for ssi in spl_si:
                if ssi[0].isupper():
                    break
                spl_file.append(ssi)
            file = '.'.join(spl_file)
            selected_tests_module.add(file)

    for item in selected_tests_module:
        print(item)


if __name__ == '__main__':
    main()
