from . import empty


class Operator:
    def __init__(self, op_name, compatible):
        self.op_name = op_name
        self.compat = compatible
        self.f = None

    def __get__(self, instance, owner):
        return self

    def __call__(self, f):
        while isinstance(f, Operator):
            f = f.f
        self.f = f
        if not hasattr(f, "names"):
            f.names = {}
        f.names[self.op_name] = self.compat
        return self

    def call(self, op, *args):
        f = self.f
        while isinstance(f, Operator):
            f = f.f
        for arg in args[1:]:
            if arg and not any(x in f.names[op] for x in arg.inheritance()):
                return empty
        return f(*args)
