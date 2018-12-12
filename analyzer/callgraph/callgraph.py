from .pyan.visgraph import VisualGraph
from .pyan.analyzer import CallGraphVisitor
from glob import glob
import os
import json


def dump_callgraph(repo_path: str, logger=None):
    filenames = [fn for fn in glob(repo_path, recursive=True)]

    # filter upstream tests
    filenames = list(filter(lambda filename: not(filename.startswith('ecosystem' + os.path.sep + 'numpy') and
                                                 (os.path.sep + 'tests' + os.path.sep in filename or
                                                 os.path.sep + 'testing' + os.path.sep in filename)), filenames))
    # filenames = ['D:\\PycharmProjects\\Type-aware-fuzzing\\REPOS\\astropy\\astropy\\convolution\\convolve.py']
    # filenames = ['D:\\PycharmProjects\\regression-test\\test.py']
    visitor = CallGraphVisitor(filenames, logger=logger)
    graph = VisualGraph.dump_callgraph(visitor, logger=logger)
    with open('callgraph.json', mode='w', encoding='utf-8') as wf:
        wf.write(
            json.dumps(graph,
                       default=lambda o: {
                           "namespace": o.__dict__["namespace"],
                           "name": o.__dict__["name"],
                           "flavor": o.__dict__["flavor"]
                       },
                       indent=4)
        )
    return graph
