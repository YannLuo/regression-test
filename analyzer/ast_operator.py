import ast
import astor


class FunctionDef(object):
    def __init__(self):
        self.file = None
        self.name = None
        self.start_lineno = 0

    def __str__(self):
        return f'FunctionDef<file: {self.file}  name: {self.name}  lineno: {self.start_lineno}>'

    def __repr__(self):
        return f'FunctionDef<file: {self.file}  name: {self.name}  lineno: {self.start_lineno}>'

    def __lt__(self, other):
        return self.start_lineno < other.start_lineno


class FunctionDefVisitor(ast.NodeVisitor):
    def __init__(self, file):
        self.file = file
        self.functiondef_list = []

    def visit_FunctionDef(self, node):
        entry = FunctionDef()
        entry.file = self.file
        entry.name = node.name
        entry.start_lineno = node.lineno
        self.functiondef_list.append(node)
        self.generic_visit(node)


def collect_functiondef(fp: str):
    root = astor.parse_file(fp)
    with open(fp, mode='r', encoding='utf-8') as rf:
        lines = rf.readlines()
    line_cnt = len(lines)
    functiondef_list = []
    for node in root.body:
        if isinstance(node, ast.FunctionDef):
            entry = FunctionDef()
            entry.file = fp
            entry.name = node.name
            entry.start_lineno = node.lineno
            functiondef_list.append(entry)
        elif isinstance(node, ast.ClassDef):
            for n in node.body:
                if isinstance(n, ast.FunctionDef):
                    entry = FunctionDef()
                    entry.file = fp
                    entry.name = n.name
                    entry.start_lineno = n.lineno
                    functiondef_list.append(entry)
    EOF_entry = FunctionDef()
    EOF_entry.file = fp
    EOF_entry.name = '__EOF__'
    EOF_entry.start_lineno = line_cnt + 1
    functiondef_list.append(EOF_entry)
    return sorted(functiondef_list)
