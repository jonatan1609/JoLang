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
        return f"ast.{self.__class__.__name__}({self.format_args()})"

    def __eq__(self, other):
        if not type(self) is type(other):
            return False
        params = inspect.signature(self.__init__).parameters.keys()
        return all((getattr(self, param) == getattr(other, param)) for param in params)

class Operator(Ast):
    def __init__(self, line, column):
        self.line = line
        self.column = column


class Node(Ast):
    def __init__(self, line, column, argument=None):
        self.line = line
        self.column = column
        self.argument = argument


class BinaryNode(Ast):
    def __init__(self, line, column, left, op, right):
        self.line = line
        self.column = column
        self.left = left
        self.op = op
        self.right = right


class Container(Ast):
    def __init__(self, line, column, items):
        self.line = line
        self.column = column
        self.items = items


class Attribute(Ast):
    def __init__(self, line, column, obj, attribute):
        self.line = line
        self.column = column
        self.obj = obj
        self.attribute = attribute


class If(Ast):
    def __init__(self, line, column, condition, body, elifs, else_block):
        self.line = line
        self.column = column
        self.condition = condition
        self.body = body
        self.elifs = elifs
        self.else_block = else_block


class While(Ast):
    def __init__(self, line, column, condition, body):
        self.line = line
        self.column = column
        self.condition = condition
        self.body = body


class For(Ast):
    def __init__(self, line, column, parts, body):
        self.line = line
        self.column = column
        self.parts = parts
        self.body = body


class Call(Ast):
    def __init__(self, line, column, name: "Name", args: "Arguments"):
        self.line = line
        self.column = column
        self.name = name
        self.args = args


class Body(Ast):
    def __init__(self, line, column, statements: typing.List["Statement"]):
        self.line = line
        self.column = column
        self.statements = statements


class Assignment(Ast):
    def __init__(self, line, column, name, op, content):
        self.line = line
        self.column = column
        self.name = name
        self.op = op
        self.content = content


class Function(Ast):
    def __init__(self, line: int, column: int, name: "Name", params: "Arguments", body):
        self.line = line
        self.column = column
        self.name = name
        self.params = params
        self.body = body


class Index(Ast):
    def __init__(self, line: int, column: int, start, end, step, obj):
        self.line = line
        self.column = column
        self.start = start
        self.end = end
        self.step = step
        self.obj = obj

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
class Spaceship(Operator): pass
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


class Integer(Node): pass
class Float(Node): pass
class UnaryTilde(Node): pass
class UnaryAdd(Node): pass
class UnarySubtract(Node): pass
class UnaryLogicalNot(Node): pass
class String(Node): pass
class Name(Node): pass
class Return(Node): pass
class Break(Node): pass
class Continue(Node): pass

# containers


class Array(Container): pass
class Arguments(Container): pass

# binary nodes (two-argument nodes)

class Compare(BinaryNode): pass

