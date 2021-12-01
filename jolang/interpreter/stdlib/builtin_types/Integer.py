from .object import Object
from .operator import Operator
from .String import String


class Integer(Object):
    def __init__(self, number):
        super().__init__()
        self._obj = number

    @Operator("UnarySubtract", compatible=["Integer"])
    def unary_subtract(self):
        return Integer(-self._obj)

    @Operator("UnaryAdd", compatible=["Integer"])
    def unary_add(self):
        return Integer(+self._obj)

    @Operator("UnaryTilde", compatible=["Integer"])
    def unary_tilde(self):
        return Integer(~self._obj)

    @Operator("InplaceAdd", compatible=["Integer"])
    @Operator("Add", compatible=["Integer"])
    def add(self, other):
        return Integer(self._obj + other._obj)

    @Operator("InplaceSubtract", compatible=["Integer"])
    @Operator("Subtract", compatible=["Integer"])
    def subtract(self, other):
        return Integer(self._obj - other._obj)

    @Operator("InplaceDivide", compatible=["Integer"])
    @Operator("Divide", compatible=["Integer"])
    def divide(self, other):
        return Integer(self._obj / other._obj)

    @Operator("InplaceMultiply", compatible=["Integer"])
    @Operator("Multiply", compatible=["Integer", "String"])
    def multiply(self, other):
        if isinstance(other, String):
            restype = String
        else:
            restype = Integer
        return restype(self._obj * other._obj)

    @Operator("InplaceModulo", compatible=["Integer"])
    @Operator("Modulo", compatible=["Integer"])
    def modulo(self, other):
        return Integer(self._obj % other._obj)

    @Operator("InplaceLessEqual", compatible=["Integer"])
    @Operator("LessEqual", compatible=["Integer"])
    def less_equal(self, other):
        return Integer(self._obj <= other._obj)

    @Operator("InplaceGreatEqual", compatible=["Integer"])
    @Operator("GreatEqual", compatible=["Integer"])
    def great_equal(self, other):
        return Integer(self._obj >= other._obj)

    @Operator("InplaceGreaterThan", compatible=["Integer"])
    @Operator("GreaterThan", compatible=["Integer"])
    def greater_than(self, other):
        return Integer(self._obj > other._obj)

    @Operator("InplaceLesserThan", compatible=["Integer"])
    @Operator("LesserThan", compatible=["Integer"])
    def lesser_than(self, other):
        return Integer(self._obj < other._obj)

    @Operator("InplaceOr", compatible=["Integer"])
    @Operator("Or", compatible=["Integer"])
    def or_(self, other):
        return Integer(self._obj | other._obj)

    @Operator("InplaceAnd", compatible=["Integer"])
    @Operator("And", compatible=["Integer"])
    def and_(self, other):
        return Integer(self._obj & other._obj)

    @Operator("InplaceXor", compatible=["Integer"])
    @Operator("Xor", compatible=["Integer"])
    def xor(self, other):
        return Integer(self._obj ^ other._obj)

    @Operator("InplaceLeftShift", compatible=["Integer"])
    @Operator("LeftShift", compatible=["Integer"])
    def left_shift(self, other):
        return Integer(self._obj << other._obj)

    @Operator("InplaceRightShift", compatible=["Integer"])
    @Operator("RightShift", compatible=["Integer"])
    def right_shift(self, other):
        return Integer(self._obj >> other._obj)
