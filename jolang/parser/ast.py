import inspect
import typing


class Ast:
    @staticmethod
    def format_arg(argument):
        if isinstance(argument, str):
            return repr(argument)
        return argument

    def format_args(self):
        return ", ".join(f"{x}={self.format_arg(getattr(self, x, None))}" for x in inspect.signature(self.__init__).parameters)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.format_args()})"


class Operator(Ast):
    def __init__(self):
        pass


class Node(Ast):
    def __init__(self, argument):
        self.argument = argument


class BinaryNode(Ast):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Container(Ast):
    def __init__(self, items):
        self.items = items


class Call(Ast):
    def __init__(self, name: "Name", args: "Arguments"):
        self.name = name
        self.args = args


class Body(Ast):
    def __init__(self, statements: typing.List["Statement"]):
        self.statements = statements


class Assignment(Ast):
    def __init__(self, name, op, content):
        self.name = name
        self.op = op
        self.content = content


class Cast(Ast):
    def __init__(self, obj, typ):
        self.obj = obj
        self.typ = typ


# operators

class Add(Operator): pass
class Subtract(Operator): pass
class Divide(Operator): pass
class Multiply(Operator): pass
class Modulo(Operator): pass
class Equals(Operator): pass
class NotEqual(Operator): pass
class LessEqual(Operator): pass
class GreatEqual(Operator): pass
class GreaterThan(Operator): pass
class LesserThan(Operator): pass
class LogicOr(Operator): pass
class LogicAnd(Operator): pass
class Xor(Operator): pass
class Or(Operator): pass
class And(Operator): pass
class LeftShift(Operator): pass
class RightShift(Operator): pass
class Assign(Operator): pass
class InplaceAdd(Operator): pass
class InplaceSubtract(Operator): pass
class InplaceModulo(Operator): pass
class InplaceMultiply(Operator): pass
class InplaceDivide(Operator): pass
class InplaceRightShift(Operator): pass
class InplaceLeftShift(Operator): pass
class InplaceBinOr(Operator): pass
class InplaceBinAnd(Operator): pass
class InplaceXor(Operator): pass

# nodes (one-argument nodes)


class Number(Node): pass
class UnaryTilde(Node): pass
class UnaryAdd(Node): pass
class UnarySubtract(Node): pass
class UnaryLogicalNot(Node): pass
class String(Node): pass
class Name(Node): pass


# containers


class Array(Container): pass
class Arguments(Container): pass

# binary nodes (two-argument nodes)

class Compare(BinaryNode): pass
