from .scope import Scope, LoopScope, Frame, FuncScope
from .errors import NameError, StackCall, OperatorError, RuntimeError, make_stack
from ..parser import ast
from .stdlib.builtin_types.Integer import Integer, Float
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

        NameError(f"{node.argument!r} doesn't exist in the current scope", stack=make_stack(self.file, node, scope)).throw()

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
        obj = self.eval(node.argument, scope)
        result = obj.operate(node.__class__.__name__)
        if result is empty:
            OperatorError(f"Can't {node.__class__.__name__} with {obj.__class__.__name__!r}", stack=[
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
            name = self.eval(node.name, scope)
            f_scope = f.scope.merge(Scope(name, dict(zip([x.argument for x in f.parameters], [self.eval(arg, scope) for arg in node.args.items if arg]))))
            f_scope.func = FuncScope(name)
            # exec body of func within the scope
            for statement in f.body:
                self.eval(statement, f_scope)
                if not f_scope.func.active:
                    ret = f_scope.func.ret
                    break
        return ret

    def eval_if(self, node, scope):
        condition = self.eval(node.condition, scope)._obj
        success = False
        if condition:
            success = True
            for statement in node.body:
                self.eval(statement, scope)
        if not success:
            for elif_node in node.elifs:
                self.eval_if(elif_node, scope)
        if not success and node.else_block:
            for statement in node.else_block:
                self.eval(statement, scope)

    def eval_for(self, node, scope):
        loop = LoopScope("x")  # for future use so we can break via its name (break x)
        new_scope = scope.merge(Scope(scope.name, loop=loop, func=scope.func))
        self.eval(node.parts[0], new_scope)
        for_scope = scope.merge(new_scope)

        while True:
            condition = self.eval(node.parts[1], for_scope)
            if condition:
                if not condition._obj:
                    break
                for statement in node.body:
                    if loop.continue_:
                        loop.continue_ = False
                        continue
                    if not loop.active:
                        break
                    self.eval(statement, for_scope)
                else:
                    self.eval(node.parts[2], for_scope)
                    continue
                break


    def eval_while(self, node, scope):
        loop = LoopScope("x")  # for future use so we can break via its name (break x)
        loop_scope = scope.merge(Scope(scope.name, loop=loop, func=scope.func))
        while True:
            condition = self.eval(node.condition, loop_scope)
            if not condition._obj:
                break
            for statement in node.body:
                if loop.continue_:
                    loop.continue_ = False
                    continue
                if not loop.active:
                    break
                self.eval(statement, loop_scope)
            else:
                continue
            break

    def eval(self, node=None, scope=None):
        if not node:
            node = self.node
        if not scope:
            scope = self.scope
        if scope.func and not scope.func.active:
            return Null()
        if scope.loop and (not scope.loop.active or scope.loop.continue_):
            return Null()
        if isinstance(node, ast.Body):
            for statement in node.statements:
                self.eval(statement, scope)
        elif isinstance(node, ast.Continue):
            scope.loop.continue_ = True
            return node
        elif isinstance(node, ast.Break):
            scope.loop.active = False
            return node
        elif isinstance(node, ast.Return):
            scope.func.ret = Null()
            if node.argument:
                scope.func.ret = self.eval(node.argument, scope)
            scope.func.active = False
            return scope.func.ret
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
        elif isinstance(node, ast.Float):
            return Float(node.argument)
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
        elif isinstance(node, ast.If):
            return self.eval_if(node, scope)
        elif isinstance(node, ast.While):
            return self.eval_while(node, scope)
        elif isinstance(node, ast.For):
            return self.eval_for(node, scope)
# todo: make stdlib operators, call stack, declaration operator.
