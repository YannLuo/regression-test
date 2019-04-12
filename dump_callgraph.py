import os
import json
from collections import defaultdict


REPOS = ["astropy", "ccdproc", "dask", "gammapy", "h5py", "IPython", "joblib", "matplotlib", "nbconvert",
         "networkx", "nilearn", "numexpr", "numpy", "obspy", "pandas", "scipy", "seaborn", "skbio", "sklearn",
         "specutils", "statsmodels", "sympy", "tables", "theano", "xarray", "photutils", "asdf", "poppy", "astropy_helpers",
         "bottleneck", "pyregion", "brian2", "naima", "pyamg", "patsy", "astroplan", "radio_beam", "numba", 
         "mahotas", "eliot", "randomgen", "shared_ndarray", "nrrd", "autoptim", "sparse",
         "alphalens", "pyjet", "numbagg", "cvxpy", "aplpy", "numpydoc", "deap", "mpmath",
         "oct2py", "atpy", "gwcs", "pymc3", "starfish", "verde", "pooch",
         "astroimtools", "stginga", "synphot", "pydl",
         "iexfinance", "plydata", "ibis"][-1:]
UPSTREAM_DICT = {
    "astropy": "scipy",
    "ccdproc": "scipy",
    "dask": "scipy",
    "gammapy": "astropy",
    "h5py": "numpy",
    "IPython": "numpy",
    "joblib": "numpy",
    "matplotlib": "numpy",
    "nbconvert": "$",
    "networkx": "scipy",
    "nilearn": "scipy",
    "numba": "scipy",
    "numexpr": "numpy",
    "numpy": "$",
    "obspy": "scipy",
    "pandas": "scipy",
    "scipy": "numpy",
    "seaborn": "scipy",
    "skbio": "scipy",
    "sklearn": "scipy",
    "specutils": "scipy",
    "statsmodels": "scipy",
    "sympy": "scipy",
    "tables": "numpy",
    "theano": "scipy",
    "xarray": "scipy",
    "photutils": "scipy",
    "asdf": "numpy",
    "poppy": "scipy",
    "astropy_helpers": "numpy",
    "bottleneck": "numpy",
    "pyregion": "numpy",
    "brian2": "numpy",
    "naima": "scipy",
    "pyamg": "scipy",
    "patsy": "numpy",
    "astroplan": "numpy",
    "radio_beam": "numpy",
    "randomgen": "scipy",
    "shared_ndarray": "numpy",
    "eliot": "numpy",
    "mahotas": "scipy",
    "nrrd": "numpy",
    "autoptim": "numpy",
    "sparse": "scipy",
    "alphalens": "scipy",
    "pyjet": "numpy",
    "numbagg": "numpy",
    "cvxpy": "scipy",
    "aplpy": "scipy",
    "numpydoc": "numpy",
    "deap": "numpy",
    "mpmath": "numpy",
    "oct2py": "scipy",
    "atpy": "numpy", 
    "gwcs": "scipy",
    "pymc3": "scipy",
    "verde": "scipy",
    "pooch": "numpy",
    "astroimtools": "astropy",
    "stginga": "astropy",
    "synphot": "astropy",
    "pydl": "astropy",
    "iexfinance": "numpy",
    "plydata": "numpy",
    "ibis": "numpy"
}


def read_call_trace(cg_file):
    with open(cg_file, mode="r", encoding="utf-8") as rf:
        lines = rf.readlines()
    trace = [line.strip().split('$') for line in lines]
    return trace


def dump_one_repo(repo):
    trace = read_call_trace(os.path.join(
        "traces", "%s_trace.txt" % (repo, )))
    downstream = repo
    upstream = UPSTREAM_DICT[repo]

    callgraph = defaultdict(set)
    rev_callgraph = defaultdict(set)
    for line in trace:
        caller, callee = line
        if (caller.startswith(upstream) and callee.startswith(upstream)) or \
                (caller.startswith(downstream) and any([callee.startswith(x) for x in (downstream, upstream)])) or \
                (upstream == "scipy" and (
                    caller.startswith(UPSTREAM_DICT[upstream]) and callee.startswith(UPSTREAM_DICT[upstream]) or
                    caller.startswith(upstream) and callee.startswith(UPSTREAM_DICT[upstream]) or
                    caller.startswith(downstream) and callee.startswith(
                        UPSTREAM_DICT[upstream])
                )) or \
                (upstream == "astropy" and (
                    caller.startswith(UPSTREAM_DICT[UPSTREAM_DICT[upstream]]) and callee.startswith(UPSTREAM_DICT[UPSTREAM_DICT[upstream]]) or
                    caller.startswith(UPSTREAM_DICT[upstream]) and callee.startswith(UPSTREAM_DICT[UPSTREAM_DICT[upstream]]) or
                    caller.startswith(upstream) and callee.startswith(UPSTREAM_DICT[UPSTREAM_DICT[upstream]]) or 
                    caller.startswith(downstream) and callee.startswith(UPSTREAM_DICT[UPSTREAM_DICT[upstream]])
                )):
            rev_callgraph[callee].add(caller)
            callgraph[caller].add(callee)
    for k in rev_callgraph:
        rev_callgraph[k] = list(rev_callgraph[k])
    for k in callgraph:
        callgraph[k] = list(callgraph[k])
    with open(os.path.join("callgraph", "%s_callgraph.json" % (repo, )), mode="w", encoding="utf-8") as wf:
        json.dump(callgraph, wf, default=lambda o: o.__dict__, indent=4)


def main():

    for repo in REPOS:
        dump_one_repo(repo)

    # merge downstream callgraph with upstream
    for repo in REPOS:
        downs = repo
        ups = UPSTREAM_DICT[repo]
        callgraph = defaultdict(set)

        with open(os.path.join("callgraph", "%s_callgraph.json" % (downs, )), mode="r", encoding="utf-8") as rf:
            j = json.load(rf)
        for k in j:
            for vi in j[k]:
                callgraph[k].add(vi)

        if ups != "$":
            with open(os.path.join("callgraph", "%s_callgraph.json" % (ups, )), mode="r", encoding="utf-8") as rf:
                j = json.load(rf)
            for k in j:
                for vi in j[k]:
                    callgraph[k].add(vi)
        if ups == "scipy":
            with open(os.path.join("callgraph", "%s_callgraph.json" % (UPSTREAM_DICT[ups], )), mode="r", encoding="utf-8") as rf:
                j = json.load(rf)
            for k in j:
                for vi in j[k]:
                    callgraph[k].add(vi)

        for k in callgraph:
            callgraph[k] = list(callgraph[k])
        with open(os.path.join("merged_callgraph", "%s_callgraph.json" % (repo, )), mode="w", encoding="utf-8") as wf:
            json.dump(callgraph, wf, default=lambda o: o.__dict__, indent=4)

        rev_callgraph = defaultdict(set)
        for k in callgraph:
            for vi in callgraph[k]:
                rev_callgraph[vi].add(k)
        for k in rev_callgraph:
            rev_callgraph[k] = list(rev_callgraph[k])
        with open(os.path.join("merged_callgraph", "%s_rev_callgraph.json" % (repo, )), mode="w", encoding="utf-8") as wf:
            json.dump(rev_callgraph, wf,
                      default=lambda o: o.__dict__, indent=4)


if __name__ == "__main__":
    main()
