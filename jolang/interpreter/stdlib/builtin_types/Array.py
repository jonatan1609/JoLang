from .object import Object
from .operator import Operator


class Array(Object):
    def __init__(self, items):
        super().__init__()
        self._obj = items

    @Operator("Index", compatible=["Integer"])
    def index(self, start, stop, step):
        if start and not (stop or step):
            return self._obj[getattr(start, "_obj", None)]
        return Array(self._obj[getattr(start, "_obj", None):getattr(stop, "_obj", None):getattr(step, "_obj", None)])

    def __str__(self):
        return str(self._obj)