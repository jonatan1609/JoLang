from .builtin import BuiltinType
from .operator import Operator
from . import empty


class Object(BuiltinType):
    def __init__(self):
        self.operators = self.__find_operators()
        self._obj = None

    def __find_operators(self):
        return {
            name: op_.call
            for op in dir(self) if isinstance(op_ := getattr(self, op), Operator) and not op.startswith("_") for name in op_.f.names
        }

    def operate(self, op, *args):
        if not (op := self.available_operator(op)):
            return empty
        else:
            return self.__do_operate(op, *args)

    def available_operator(self, op):
        if not self.operators:
            self.operators = self.__find_operators()
        if op := self.operators.get(op):
            return op

    def __do_operate(self, op, *args):
        return op(self, *args)

    def inheritance(self):
        return [cls.__name__ for cls in self.__class__.mro()]

    @Operator("Equals", compatible=["Object"])
    def equals(self, other):
        return self._obj == other._obj

    @Operator("NotEqual", compatible=["Object"])
    def not_equal(self, other):
        return self._obj != other._obj

    @Operator("UnaryLogicalNot", compatible=["Object"])
    def unary_logical_not(self):
        return not self._obj
