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
            f.names = []
        f.names.append(self.op_name)
        return self

    def call(self, *args):
        for arg in args:
            if not any(x in self.compat for x in arg.inheritance()):
                return empty
        f = self.f
        while isinstance(f, Operator):
            f = f.f
        return f(*args)
