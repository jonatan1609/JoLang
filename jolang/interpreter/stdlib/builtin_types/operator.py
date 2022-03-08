from . import empty
import inspect


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


class Attribute:
    function = Function = ...

    def __init__(self, op_name):
        self.op_name = op_name
        self._obj = self

    def __call__(self, function):
        function.attr = self.op_name
        self.f = function
        self.function = Attribute.Function(self.op_name, py_bind=self.func, method_of=function.__module__.rsplit(".", 1)[-1], restype=empty)
        return self

    def init(self, obj):
        self.obj = obj

    def func(self, *items):
        if len(inspect.getfullargspec(self.f).args) - 1 != len(items):
            return empty, f"{self.f.attr!r} requires {len(inspect.getfullargspec(self.f).args) - 1} arguments but {len(items)} arguments were supplied",
        return self.f(self.obj, *items)

    def __repr__(self):
        return str(self.function)
