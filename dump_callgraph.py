import os
import json
from collections import defaultdict


REPOS = ["numpy", "astropy", "theano", "numba", "obspy", "asdf", "ccdproc"]
UPSTREAM_DICT = {
    "numpy": "numpy",
    "astropy": "numpy",
    "theano": "numpy",
    "numba": "numpy",
    "obspy": "numpy",
    "asdf": "astropy",
    "ccdproc": "astropy"
}


def read_call_trace(cg_file):
    with open(cg_file, mode="r", encoding="utf-8") as rf:
        lines = rf.readlines()
    trace = [line.strip().split() for line in lines]
    return trace


def archive_one_cg(repo, rev_callgraph):
    with open(os.path.join("callgraph", "%s_rev_callgraph.json" % (repo, )), mode="w", encoding="utf-8") as wf:
        wf.write(
            json.dumps(rev_callgraph,
                       default=lambda o: o.__dict__,
                       indent=4)
        )


def dump_one_cg(repo):
    trace = read_call_trace(os.path.join(
        "callgraph", "%s_trace.txt" % (repo, )))
    downstream = repo + "."
    upstream = UPSTREAM_DICT[repo] + "."
    rev_callgraph = defaultdict(set)
    try:
        for caller, callee in trace:
            if (caller.startswith(upstream) and callee.startswith(upstream)) or \
                    (caller.startswith(downstream) and any([callee.startswith(x) for x in (downstream, upstream)])):
                rev_callgraph[callee].add(caller)
    except:
        print(repo)
    for k in rev_callgraph:
        rev_callgraph[k] = list(rev_callgraph[k])
    archive_one_cg(repo, rev_callgraph)


def main():
    for repo in REPOS:
        dump_one_cg(repo)


if __name__ == "__main__":
    main()
