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


class Add(Operator):
    pass


class Subtract(Operator):
    pass


class Divide(Operator):
    pass


class Multiply(Operator):
    pass


class Number(Node):
    pass


class UnaryTilde(Node):
    pass


class UnaryAdd(Node):
    pass


class UnarySubtract(Node):
    pass


class UnaryLogicalNot(Node):
    pass


class String(Node):
    pass


class Constant(Node):
    pass


class Modulo(Operator):
    pass


class Container(Ast):
    def __init__(self, items):
        self.items = items


class Array(Container):
    pass


class Statement(Ast):
    pass


class Arguments(Container):
    pass


class Call(Ast):
    def __init__(self, const: Constant, args: Arguments):
        self.const = const
        self.args = args


class Body(Ast):
    def __init__(self, statements: typing.List[Statement]):
        self.statements = statements


class Assignment(Ast):
    def __init__(self, const, content):
        self.const = const
        self.content = content


class Cast(Ast):
    def __init__(self, obj, typ):
        self.obj = obj
        self.typ = typ
