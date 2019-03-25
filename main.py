from analyzer.diff_parser import parse_diff
from analyzer.ast_operator import collect_functiondef
import git
import os
import json


def get_modified_functions(commit_sha):
    repo_path = os.path.join('REPOS', 'numpy')
    repo = git.Repo(repo_path)
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
            functiondef_list = collect_functiondef(
                os.path.join(repo_path, tar_file_path))
            for add_lineno in diff.hunk_infos["a"]:
                for i in range(len(functiondef_list) - 1):
                    if functiondef_list[i].start_lineno <= add_lineno < functiondef_list[i + 1].start_lineno:
                        mod_functiondef_list.add(
                            (tar_module, functiondef_list[i].name))
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
            functiondef_list = collect_functiondef(
                os.path.join(repo_path, src_file_path))
            for del_lineno in diff.hunk_infos["d"]:
                for i in range(len(functiondef_list) - 1):
                    if functiondef_list[i].start_lineno <= del_lineno < functiondef_list[i + 1].start_lineno:
                        mod_functiondef_list.add(
                            (src_module, functiondef_list[i].name))
        try:
            repo.git.checkout(['-f', 'master'])
        except:
            pass

    return mod_functiondef_list


upstream = "numpy"
downstream = "astropy"


def main():
    # ========== analyze git diff and dump modified function/method ==========

    mod_functiondef_list = get_modified_functions("a859ace")

    # ========== analyze change impact (Regression Testing Selection) ==========

    with open(os.path.join("merged_callgraph", "%s_rev_callgraph.json" % (downstream, )), mode='r', encoding='utf-8') as rf:
        rev_callgraph = json.load(rf)

    # 统计测试文件数
    # test_files = set()
    # for caller, callees in rev_callgraph.items():
    #     if ".tests." in caller and caller.startswith('astropy') and "test_" in caller:
    #         spl_file = []
    #         spl_cs = caller.split('.')[:-1]
    #         for ssi in spl_cs:
    #             if ssi[0].isupper():
    #                 break
    #             spl_file.append(ssi)
    #         file = '.'.join(spl_file)
    #         test_files.add(file)
    #     for callee in callees:
    #         if ".tests." in callee and callee.startswith('astropy') and "test_" in callee:
    #             spl_file = []
    #             spl_cs = callee.split('.')[:-1]
    #             for ssi in spl_cs:
    #                 if ssi[0].isupper():
    #                     break
    #                 spl_file.append(ssi)
    #             file = '.'.join(spl_file)
    #             test_files.add(file)
    # print(len(test_files))

    s = set()
    q = []
    for prefix_namespace, name in mod_functiondef_list:
        for cur_call in rev_callgraph:
            if cur_call.startswith(prefix_namespace) and cur_call.split('.')[-1] == name and cur_call not in s:
                if cur_call not in s:
                    q.append(cur_call)
                    s.add(cur_call)

    while len(q):
        top = q[0]
        q = q[1:]
        if top in rev_callgraph:
            for si in rev_callgraph[top]:
                if si not in s and all(ch not in si for ch in ("(", "#", "<", "__init__")):
                    q.append(si)
                    s.add(si)

    selected_tests_module = set()
    for si in s:
        if ".tests." in si and si.startswith(downstream + ".") and "test_" in si:
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
