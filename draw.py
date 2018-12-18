from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import json
from pyecharts import Graph
import csv


def draw1():
    global q
    DG = nx.DiGraph()
    nodes = set()
    edges = set()

    while len(q):
        top = q[0]
        q = q[1:]
        spl_file = []
        spl_si = top.split('.')[:-1]
        for ssi in spl_si:
            if ssi[0].isupper():
                break
            spl_file.append(ssi)
        file = '.'.join(spl_file)
        nodes.add(file)
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
                    file1 = '.'.join(spl_file)
                    edges.add((file, file1))

    nodes = list(nodes)
    colors = []
    for node in nodes:
        if node == 'numpy.ma.extras' or node == 'numpy.ma.core':
            colors.append('red')
        elif node.startswith('numpy'):
            colors.append('orange')
        elif node.startswith('astropy') and '.tests.' not in node:
            colors.append('blue')
        else:
            colors.append('green')
    edges = list(edges)
    DG.add_nodes_from(nodes)
    DG.add_edges_from(edges)
    nx.draw(DG, node_size=20, node_color=colors, width=0.5)
    plt.show()


def draw2():
    global q
    nodes = set()
    edges = set()

    while len(q):
        top = q[0]
        q = q[1:]
        spl_file = []
        spl_si = top.split('.')[:-1]
        for ssi in spl_si:
            if ssi[0].isupper():
                break
            spl_file.append(ssi)
        file = '.'.join(spl_file)
        nodes.add(file)
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
                    file1 = '.'.join(spl_file)
                    edges.add((file, file1))

    nodes = list(nodes)
    edges = list(edges)
    new_nodes = []
    for node in nodes:
        if node == 'numpy.ma.extras' or node == 'numpy.ma.core':
            c = 0
            size = 30
        elif node.startswith("numpy"):
            c = 1
            size = 20
        elif node.startswith("astropy") and ".tests." not in node:
            c = 2
            size = 20
        else:
            c = 3
            size = 10
        new_nodes.append({
            "symbolSize": size,
            "name": node,
            "category": c
        })
    nodes = new_nodes
    edges = [{"source": item[0], "target":item[1]} for item in edges]
    # graph = Graph("调用图", width=1600, height=1200, title_pos="center")
    # graph.add("", nodes, edges,  graph_edge_symbol=[None, 'arrow'],
    #           graph_gravity=0.10, graph_repulsion=50, graph_edge_length=50,
    #           categories=['start', 'numpy', 'astropy', 'astropy_test'], is_legend_show=True)
    # graph.render()
    with open('nodes.csv', mode='w', encoding='utf-8', newline='') as wf:
        writer = csv.writer(wf)
        writer.writerow(('Id', 'Label'))
        for node in nodes:
            writer.writerow((node["name"], node["category"]))
    with open('edges.csv', mode='w', encoding='utf-8', newline='') as wf:
        writer = csv.writer(wf)
        writer.writerow(('source', 'target'))
        for edge in edges:
            writer.writerow((edge["source"], edge["target"]))


callgraph = defaultdict(set)
with open("astropy_callgraph.txt", mode="r", encoding="utf-8") as rf:
    lines = rf.readlines()
for line in lines:
    src, dst = line.strip().split()
    if (src.startswith("numpy") or src.startswith("astropy")) and (dst.startswith("numpy") or dst.startswith("astropy")):
        callgraph[src].add(dst)

q = ['numpy.ma.core.MaskedArray.sort', 'numpy.ma.core.sort', 'numpy.ma.extras._median']
s = set()
for qi in q:
    s.add(qi)

with open('rev_callgraph.json', mode='r', encoding='utf-8') as rf:
    rev_callgraph = json.load(rf)

# draw1()

draw2()
