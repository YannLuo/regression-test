import os
from logger import create_logger
import time
from analyzer.callgraph.callgraph import dump_callgraph


def generate_callgraph():
    logger = create_logger('log.log')

    repo_path = os.path.join('ecosystem', '**', '*.py')
    stt = time.clock()
    callgraph = dump_callgraph(repo_path, logger=logger)
    edt = time.clock()
    print("Generate callgraph cost %.2f minutes." % ((edt - stt) / 60.0, ))
    return callgraph
