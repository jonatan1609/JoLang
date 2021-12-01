from .scope import Scope
from .errors import NameError, StackCall, OperatorError, RuntimeError
from ..parser import ast
from .stdlib.builtin_types.Integer import Integer
from .stdlib.builtin_types.String import String
from .stdlib.builtin_types.Null import Null
from .stdlib.builtin_types import empty
from .stdlib.std_functions.functions import functions
from .stdlib.builtin_types.Function import Function
from .stdlib.builtin_types.Boolean import Boolean


class Interpreter:
    def __init__(self, file):
        self.file = file
        self.node = file.ast
        self.scope = Scope("module", functions)

    def eval_function(self, node, scope):
        name = node.name.argument
        params = node.params.items
        scope.register(name, Function(name, params, node.body, scope=scope))

    def eval_name(self, node, scope):
        if scope.has(node.argument):
            return scope.get(node.argument)
        NameError(f"{node.argument!r} doesn't exist in the current scope", stack=[
            StackCall(self.file.name, node.line, node.column, repr(scope), self.file.line(node.line))
        ]).throw()

    def eval_assignment(self, node, scope):
        res = Null()
        if isinstance(node.op, ast.Assign):
            scope.register(node.name.argument, self.eval(node.content, scope))
        else:
            if scope.has(node.name.argument):
                res = self.eval(node.content, scope)
                if (res := scope.get(node.name.argument).operate(node.op.__class__.__name__, res)) is empty:
                    OperatorError(f"Can't {node.op.__class__.__name__} "
                                  f"with {scope.get(node.name.argument).__class__.__name__!r} and {res.__class__.__name__!r}", stack=[
                        StackCall(self.file.name, node.line, node.column, repr(scope), self.file.line(node.line))
                    ]).throw()
                scope.register(node.name.argument, res)
            else:
                NameError(f"{node.name.argument!r} doesn't exist in the current scope", stack=[
                    StackCall(self.file.name, node.line, node.column, repr(scope), self.file.line(node.line))
                ]).throw()
        return res

    def eval_binary_node(self, node, scope):
        left, right = self.eval(node.left, scope), self.eval(node.right, scope)
        result = left.operate(node.op.__class__.__name__, right)

        if result is empty:
            OperatorError(f"Can't {node.op.__class__.__name__} "
                          f"with {left.__class__.__name__!r} and {right.__class__.__name__!r}", stack=[
                StackCall(self.file.name, node.line, node.column, repr(scope), self.file.line(node.line))
            ]).throw()
        if isinstance(node.op, (ast.NotEqual, ast.Equals)):
            return Integer(result)
        return result

    def eval_node(self, node, scope):
        if type(node) is ast.Node:
            return
        result = self.eval(node.argument, scope).operate(node.__class__.__name__)
        if result is empty:
            OperatorError(f"Can't {node.__class__.__name__} with {node.argument.__class__.__name__!r}", stack=[
                StackCall(self.file.name, node.line, node.column, repr(scope), self.file.line(node.line))
            ]).throw()
        if isinstance(node, ast.UnaryLogicalNot):
            return Boolean(result)
        return result

    def eval_call(self, node, scope):
        ret = Null()
        f = self.eval(node.name, scope)
        if f.operate("Call") is empty:
            OperatorError(f"Object of type {f.__class__.__name__!r} is not callable", stack=[
                StackCall(self.file.name, node.line, node.column, repr(scope), self.file.line(node.line))
            ]).throw()
        if not f.py_bind and len(node.args.items) != len(f.parameters):
            RuntimeError(f"{f.name} requires {len(f.parameters)} arguments but {len(node.args.items)} arguments were supplied", stack=[
                StackCall(self.file.name, node.line, node.column, repr(scope), self.file.line(node.line))
            ]).throw()
        if f.py_bind:
            ret = f.restype(f.py_bind(*[self.eval(arg, scope)._obj for arg in node.args.items if arg]))
        else:
            scope = (f.scope or scope).merge(Scope(self.eval(node.name, scope), dict(zip([x.argument for x in f.parameters], [self.eval(arg, scope) for arg in node.args.items if arg]))))
        # exec body of func within the scope
        for statement in f.body:
            if isinstance(statement, ast.Return):
                if statement.argument:
                    ret = self.eval(statement.argument, scope)
                break
            self.eval(statement, scope)
        return ret

    def eval(self, node=None, scope=None):
        if not node:
            node = self.node
        if not scope:
            scope = self.scope
        if isinstance(node, ast.Body):
            for statement in node.statements:
                self.eval(statement, scope)
        elif isinstance(node, ast.Name):
            return self.eval_name(node, scope)
        elif isinstance(node, ast.Assignment):
            return self.eval_assignment(node, scope)
        elif isinstance(node, ast.Call):
            return self.eval_call(node, scope)
        elif isinstance(node, ast.Integer):
            return Integer(node.argument)
        elif isinstance(node, ast.String):
            return String(node.argument)
        elif isinstance(node, ast.BinaryNode):
            if isinstance(node.op, ast.LogicAnd):
                res = self.eval(node.left, scope)._obj and self.eval(node.right, scope)._obj
            elif isinstance(node.op, ast.LogicOr):
                res = self.eval(node.left, scope)._obj or self.eval(node.right, scope)._obj
            else:
                res = self.eval_binary_node(node, scope)
            if isinstance(res, int):
                return Integer(res)
            elif isinstance(res, str):
                return String(res)
            return res
        elif isinstance(node, ast.Node):
            return self.eval_node(node, scope)
        elif isinstance(node, ast.Function):
            return self.eval_function(node, scope)

# todo: make stdlib operators, call stack, declaration operator.
# todo:
