import json
from main import get_modified_functions
import numpy as np
import csv
import os

with open(os.path.join("merged_callgraph", "astropy_callgraph.json"), mode='r', encoding='utf-8') as rf:
    callgraph = json.load(rf)

with open(os.path.join("merged_callgraph", "astropy_rev_callgraph.json"), mode='r', encoding='utf-8') as rf:
    rev_callgraph = json.load(rf)

mod_functiondef_list = get_modified_functions()


def approach1():
    # 根据测试用例到修改文件的调用距离排序
    s = set()
    depth_dict = {}
    q = []
    for prefix_namespace, name in mod_functiondef_list:
        for cur_call in rev_callgraph:
            if cur_call.startswith(prefix_namespace) and cur_call.split('.')[-1] == name and cur_call not in s:
                if cur_call not in s:
                    q.append(cur_call)
                    s.add(cur_call)

    q.append(-1)

    cnt = 0
    while len(q) != 1:
        top = q[0]
        q = q[1:]
        if top == -1:
            cnt += 1
            q.append(-1)
            continue
        depth_dict[top] = cnt
        if top in rev_callgraph:
            for si in rev_callgraph[top]:
                if si not in s:
                    q.append(si)
                    s.add(si)

    min_depth_dict = {}
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
            min_depth_dict[file] = min(
                min_depth_dict.setdefault(file, 99999), depth_dict[si])

    selected_tests_module = list(
        sorted(selected_tests_module, key=lambda x: min_depth_dict[x]))

    priority = np.array([min_depth_dict[x] for x in selected_tests_module])
    priority = np.exp(-priority)

    priority = priority / np.sum(priority)

    rank = 1
    with open('priority.csv', mode='w', encoding='utf-8', newline='') as wf:
        writer = csv.writer(wf)
        for i in range(len(selected_tests_module)):
            if i:
                if priority[i] != priority[i - 1]:
                    rank = i + 1
            writer.writerow(["#%d" % (rank,), selected_tests_module[i], "%.5f" % (priority[i],)])


def get_test_cases():
    test_cases = set()
    for caller, callees in callgraph.items():
        if ".tests." in caller and caller.startswith('astropy'):
            test_cases.add(caller)
        for callee in callees:
            if ".tests." in callee and callee.startswith('astropy'):
                test_cases.add(callee)
    return test_cases


def approach2_helper():

    def _helper(test_case):
        q = [test_case]
        s = set(q)
        while len(q):
            top = q[0]
            q = q[1:]
            if top in callgraph:
                for si in callgraph[top]:
                    if si not in s:
                        q.append(si)
                        s.add(si)
        return s

    test_cases = get_test_cases()
    tmp_dict = {}
    for test_case in test_cases:
        result = _helper(test_case)
        result = set([r for r in result if r.startswith('numpy.')])
        tmp_dict[test_case] = result

    # ret_dict = {}
    # for k, v in tmp_dict.items():
    #     spl_file = []
    #     spl_si = k.split('.')[:-1]
    #     for ssi in spl_si:
    #         if ssi[0].isupper():
    #             break
    #         spl_file.append(ssi)
    #     file = '.'.join(spl_file)
    #     ret_dict[file] = ret_dict.setdefault(file, set()) | v

    # for k, v in ret_dict.items():
    #     ret_dict[k] = len(v)

    ret_dict = {}
    for k, v in tmp_dict.items():
        spl_file = []
        spl_si = k.split('.')[:-1]
        for ssi in spl_si:
            if ssi[0].isupper():
                break
            spl_file.append(ssi)
        file = '.'.join(spl_file)
        ret_dict[file] = max(ret_dict.setdefault(file, 0), len(v))

    return ret_dict


def approach2():
    # 根据测试用例调用的numpy function/method数进行排序

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
                if si not in s:
                    q.append(si)
                    s.add(si)

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

    coverage_dict = approach2_helper()

    selected_tests_module = list(
        sorted(selected_tests_module, key=lambda x: -coverage_dict[x]))

    priority = np.array([coverage_dict[x] for x in selected_tests_module])
    priority = priority / np.sum(priority)

    rank = 1
    for i in range(len(selected_tests_module)):
        if i:
            if priority[i] != priority[i - 1]:
                rank = i + 1
        print("#%d" % (rank,), selected_tests_module[i], "%f" % (priority[i],))


def main():
    approach1()


if __name__ == '__main__':
    main()
