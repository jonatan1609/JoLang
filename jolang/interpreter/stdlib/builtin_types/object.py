from .builtin import BuiltinType
from .operator import Operator, Attribute
from . import empty


class Object(BuiltinType):
    def __init__(self):
        self.operators = self.__find_operators()
        self.attributes = self.__find_attributes()
        self._obj = None

    def __find_operators(self):
        return {
            name: op_.call
            for op in dir(self) if isinstance(op_ := getattr(self, op), Operator) and not op.startswith("_") for name in op_.f.names
        }

    def __find_attributes(self):
        return {getattr(self, name).op_name: getattr(self, name) for name in dir(self) if isinstance(getattr(self, name, ""), Attribute)}

    def operate(self, op_name, *args):
        if not (op := self.available_operator(op_name)):
            return empty
        else:
            return self.__do_operate(op, op_name, *args)

    def available_operator(self, op_name):
        if not self.operators:
            self.operators = self.__find_operators()
        if op := self.operators.get(op_name):
            return op

    def __do_operate(self, op, op_name, *args):
        return op(op_name, self, *args)

    def inheritance(self):
        return [cls.__name__ for cls in self.__class__.mro()]

    @Operator("GetAttr", compatible=["Object"])
    def getattr(self, attr):
        obj = self.attributes.get(attr._obj, empty)
        if obj is not empty:
            obj.init(self)
            return obj.function
        return obj

    def __repr__(self):
        return str(self._obj)

    @Operator("Equals", compatible=["Object"])
    def equals(self, other):
        return self._obj == other._obj

    @Operator("NotEqual", compatible=["Object"])
    def not_equal(self, other):
        return self._obj != other._obj

    @Operator("UnaryLogicalNot", compatible=["Object"])
    def unary_logical_not(self):
        return not self._obj

    @Operator("LogicAnd", compatible=["Object"])
    def logic_and(self, other):
        pass

    @Operator("LogicOr", compatible=["Object"])
    def logic_or(self, other):
        pass
