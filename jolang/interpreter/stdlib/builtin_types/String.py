from .object import Object
from .operator import Operator


class String(Object):
    def __init__(self, string):
        super().__init__()
        self._obj = string

    @Operator("Add", compatible=["String"])
    def add(self, other):
        return String(self._obj + other._obj)

    @Operator("Multiply", compatible=["String"])
    def multiply(self, other):
        return String(self._obj * other._obj)
