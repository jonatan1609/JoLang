class Scope:
    def __init__(self, name, namespace=None):
        self.name = name
        self.namespace = namespace or {}

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
        return Scope(other.name, {**self.namespace, **other.namespace})

    def __repr__(self):
        return f"<scope: {self.name}>"
