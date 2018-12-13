class ICall(object):
    def __init__(self, namespace, name, flavor):
        self.namespace = namespace
        self.name = name
        self.flavor = flavor
        self.indeg = 0
        self.outdeg = 0

    def __str__(self):
        return f'{self.namespace} {self.name} {self.flavor}'

    def __repr__(self):
        return f'{self.namespace} {self.name} {self.flavor}'

    def __lt__(self, other):
        return self.indeg < other.indeg

    def __eq__(self, other):
        return self.namespace == other.namespace and self.name == other.name and self.flavor == other.flavor
