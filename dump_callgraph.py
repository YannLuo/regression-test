import os
import json
from collections import defaultdict


REPOS = ["astropy", "scipy", "numpy", "pandas", "gammapy", "ccdproc", "dask",
        "h5py", "IPython", "joblib", "networkx", "nilearn", "numexpr", "obspy", "specutils",
        "statsmodels", "seaborn", "sympy", "theano", "xarray", "photutils", "asdf", 
        "pyregion", "brian2", "naima", "pyamg", "astroplan",
        "numba", "mahotas", "eliot", "randomgen",
        "sparse", "alphalens", "pyjet", "numbagg", "cvxpy", "aplpy", "deap", "mpmath",
        "oct2py", "atpy", "gwcs", "pymc3", "starfish", "verde", "pooch", "astroimtools", "stginga"
        , "pydl", "iexfinance", "plydata", "ibis"
        , "matplotlib", "sklearn", "skbio", "tables", "astropy_helpers", "patsy"
        , "radio_beam", "shared_ndarray", "nrrd", "autoptim", "synphot", "nptdms", "bottleneck", "poppy", "feets", "pvmismatch",
        "utide", "npstreams", "pyxrd", "spampy", "pyrr", "hienoi", "molml", "oommftools",
        "nnlib", "kravatte", "geometer", "slugnet", "zappy", "gfmm", "pdepy", "tidynamics",
        "texpy", "pandas_degreedays", "pyshapes", "psopy", "randnla",
        "indi", "pytablewriter", "prince", "coinsta", "kodiak", "phildb", "espandas",
        "validada", "partridge", "meza", "finta"
        , "pyik", "dicom_numpy", "json_tricks", "numpy_buffer", "datacompy", "deepgraph", "lens", "numpydoc"]
UPSTREAMS = ["numpy", "scipy", "astropy", "sklearn", "matplotlib", "pandas"]
# UPSTREAM_DICT = {
#     "astropy": "scipy",
#     "ccdproc": "scipy",
#     "dask": "scipy",
#     "gammapy": "astropy",
#     "h5py": "numpy",
#     "IPython": "numpy",
#     "joblib": "numpy",
#     "matplotlib": "numpy",
#     "nbconvert": "$",
#     "networkx": "scipy",
#     "nilearn": "scipy",
#     "numba": "scipy",
#     "numexpr": "numpy",
#     "numpy": "$",
#     "obspy": "scipy",
#     "pandas": "scipy",
#     "scipy": "numpy",
#     "seaborn": "scipy",
#     "skbio": "scipy",
#     "sklearn": "scipy",
#     "specutils": "scipy",
#     "statsmodels": "scipy",
#     "sympy": "scipy",
#     "tables": "numpy",
#     "theano": "scipy",
#     "xarray": "scipy",
#     "photutils": "scipy",
#     "asdf": "numpy",
#     "poppy": "scipy",
#     "astropy_helpers": "numpy",
#     "bottleneck": "numpy",
#     "pyregion": "numpy",
#     "brian2": "numpy",
#     "naima": "scipy",
#     "pyamg": "scipy",
#     "patsy": "numpy",
#     "astroplan": "numpy",
#     "radio_beam": "numpy",
#     "randomgen": "scipy",
#     "shared_ndarray": "numpy",
#     "eliot": "numpy",
#     "mahotas": "scipy",
#     "nrrd": "numpy",
#     "autoptim": "numpy",
#     "sparse": "scipy",
#     "alphalens": "scipy",
#     "pyjet": "numpy",
#     "numbagg": "numpy",
#     "cvxpy": "scipy",
#     "aplpy": "scipy",
#     "numpydoc": "numpy",
#     "deap": "numpy",
#     "mpmath": "numpy",
#     "oct2py": "scipy",
#     "atpy": "numpy", 
#     "gwcs": "scipy",
#     "pymc3": "scipy",
#     "verde": "scipy",
#     "pooch": "numpy",
#     "astroimtools": "astropy",
#     "stginga": "astropy",
#     "synphot": "astropy",
#     "pydl": "astropy",
#     "iexfinance": "numpy",
#     "plydata": "numpy",
#     "ibis": "numpy"
# }


def read_call_trace(cg_file):
    with open(cg_file, mode="r", encoding="utf-8") as rf:
        lines = rf.readlines()
    trace = [line.strip().split('$') for line in lines]
    return trace


def dump_one_repo(repo):
    trace = read_call_trace(os.path.join(
        "traces", "%s_trace.txt" % (repo, )))
    downstream = repo

    callgraph = defaultdict(set)
    rev_callgraph = defaultdict(set)
    for line in trace:
        caller, callee = line
        if (any([caller.startswith(x + ".") for x in REPOS]) or caller.startswith("tests.") or caller.startswith("test_") or caller.startswith("test.")) \
            and any([callee.startswith(x + ".") for x in REPOS]):
            rev_callgraph[callee].add(caller)
            callgraph[caller].add(callee)
    for k in rev_callgraph:
        rev_callgraph[k] = list(rev_callgraph[k])
    for k in callgraph:
        callgraph[k] = list(callgraph[k])
    with open(os.path.join("callgraph", "%s_callgraph.json" % (repo, )), mode="w", encoding="utf-8") as wf:
        json.dump(callgraph, wf, default=lambda o: o.__dict__, indent=4)


def main():

    # for repo in REPOS:
    #     dump_one_repo(repo)

    # merge downstream callgraph with upstream
    for repo in REPOS:
        downs = repo
        callgraph = defaultdict(set)

        with open(os.path.join("callgraph", "%s_callgraph.json" % (downs, )), mode="r", encoding="utf-8") as rf:
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
