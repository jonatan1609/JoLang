class LoopScope:
    def __init__(self, name: str):
        self.name = name
        self.active = True
        self.continue_ = False


class FunctionScope:
    pass


class Scope:
    def __init__(self, name, namespace=None, func=None, loop=None):
        self.name = name
        self.namespace = namespace or {}
        self.func = func
        self.loop = loop

    def register(self, name, content):
        self.namespace[name] = content

    def delete(self, name):
        if not self.has(name):
            pass
        del self.namespace[name]

    def has(self, name):
        return name in self.namespace

    def get(self, name):
        return self.namespace[name]

    def merge(self, other: "Scope"):
        return Scope(other.name, {**self.namespace, **other.namespace}, other.func, other.loop)

    def __repr__(self):
        return f"<scope: {self.name}>"
