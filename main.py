from analyzer.diff_parser import parse_diff
from analyzer.ast_operator import collect_functiondef
import git
import os
from select import select, select_by_coverage
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

    # 统计测试文件数
    # with open(os.path.join("merged_callgraph", "%s_rev_callgraph.json" % (downstream, )), mode='r', encoding='utf-8') as rf:
    #     rev_callgraph = json.load(rf)
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

    # selected_tests_module, traces = select(downstream, mod_functiondef_list)
    selected_tests_module, traces = select_by_coverage(downstream, mod_functiondef_list)
    for mod in selected_tests_module:
        print(mod)


if __name__ == '__main__':
    main()
