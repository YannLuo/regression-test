import ast
import astor


class FunctionDefEntry(object):
    def __init__(self):
        self.file = None
        self.name = None
        self.start_lineno = 0

    def __str__(self):
        return f'{{FunctionDefEntry\n\tfile: {self.file}\n\tname: {self.name}\n\tlineno: {self.start_lineno}\n}}'

    def __repr__(self):
        return f'{{FunctionDefEntry\n\tfile: {self.file}\n\tname: {self.name}\n\tlineno: {self.start_lineno}\n}}'

    def __lt__(self, other):
        return self.start_lineno < other.start_lineno


class FunctionDefVisitor(ast.NodeVisitor):
    def __init__(self, file):
        self.file = file
        self.functiondef_list = []

    def visit_FunctionDef(self, node):
        entry = FunctionDefEntry()
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
            entry = FunctionDefEntry()
            entry.file = fp
            entry.name = node.name
            entry.start_lineno = node.lineno
            functiondef_list.append(entry)
        elif isinstance(node, ast.ClassDef):
            for n in node.body:
                if isinstance(n, ast.FunctionDef):
                    entry = FunctionDefEntry()
                    entry.file = fp
                    entry.name = node.name
                    entry.start_lineno = node.lineno
                    functiondef_list.append(entry)
    EOF_entry = FunctionDefEntry()
    EOF_entry.file = fp
    EOF_entry.name = '__EOF__'
    EOF_entry.start_lineno = line_cnt
    functiondef_list.append(EOF_entry)
    return sorted(functiondef_list)
