import json
import os
from collections import deque


def select(downstream, upstream_mod):
    with open(os.path.join("merged_callgraph", "%s_rev_callgraph.json" % (downstream, )), mode='r', encoding='utf-8') as rf:
        rev_callgraph = json.load(rf)
    s = set()
    q = deque()
    for prefix_namespace, name in upstream_mod:
        for cur_call in rev_callgraph:
            if cur_call.startswith(prefix_namespace) and cur_call.split('.')[-1] == name and cur_call not in s:
                if cur_call not in s:
                    q.append((cur_call, [cur_call]))
                    s.add(cur_call)

    selected_tests_module = set()
    traces = {}
    while len(q):
        top, trace = q.popleft()
        if ".tests." in top and top.startswith(downstream + ".") and "test_" in top:
            spl_file = []
            spl_top = top.split('.')[:-1]
            for ssi in spl_top:
                if ssi[0].isupper():
                    break
                spl_file.append(ssi)
            file = '.'.join(spl_file)
            selected_tests_module.add(file)
            traces[top] = trace
        if top in rev_callgraph:
            for si in rev_callgraph[top]:
                if si not in s and all(ch not in si for ch in ("(", "#", "<", "__init__")):
                    q.append((si, trace + [si]))
                    s.add(si)
    return selected_tests_module, traces
