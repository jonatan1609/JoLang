import platform
import re

from jolang.tokenizer import Tokenizer
from jolang.preprocessor import preprocess
from jolang.parser import Parser, ast

print("JoLang Shell on {}".format(platform.platform()))
print("Docs: https://jolang.org")
print("Type exit or quit to close the shell")


class Evaluate:
    PATTERN = re.compile(r'(?=[A-Z])')

    def __init__(self, node: ast.Body = None):
        self.node = node
        self.variables = {}
        self.macros = {}

    @staticmethod
    def pascal_case_to_snake_case(string: str):
        return "_".join(x.lower() for x in Evaluate.PATTERN.split(string) if x)

    @staticmethod
    def visit_number(node: ast.Number):
        return node.argument

    def visit_unary_add(self, node: ast.UnaryAdd):
        return +self._visit(node.argument)

    def visit_unary_subtract(self, node: ast.UnarySubtract):
        return -self._visit(node.argument)

    def visit_unary_logical_not(self, node: ast.UnaryLogicalNot):
        return not self._visit(node.argument)

    def visit_unary_tilde(self, node: ast.UnaryTilde):
        return ~self._visit(node.argument)

    def visit_constant(self, v: ast.Constant):
        var = self.variables.get(v.argument)
        if not var:
            raise NameError(f"Variable {v.argument!r} does not exist!")
        return var

    def visit_binary_node(self, node: ast.BinaryNode):
        left, right = self._visit(node.left), self._visit(node.right)

        if isinstance(node.op, ast.Multiply):
            return left * right
        if isinstance(node.op, ast.Divide):
            return left / right
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Subtract):
            return left - right
        if isinstance(node.op, ast.Modulo):
            return left % right

    def visit_assignment(self, node: ast.Assignment):
        name = node.const.argument
        content = self._visit(node.content)
        self.variables[name] = content

    def _visit(self, node):
        method = 'visit_' + self.pascal_case_to_snake_case(node.__class__.__name__)
        method = getattr(self, method, method)
        if not callable(method):
            raise NotImplementedError(f"method {method!r} isn't implemented yet!")
        return method(node)

    @staticmethod
    def visit_string(node):
        return node.argument

    def visit_call(self, node: ast.Call):
        func = self._visit(node.const)
        args = self._visit(node.args)
        return func(*args)

    def visit_arguments(self, node: ast.Arguments):
        return [self._visit(arg) for arg in node.items]

    def visit(self):
        if self.node.statements:
            return self._visit(self.node.statements[0])
        return ''


evaluator = Evaluate()


def main(code: str):
    stream = Tokenizer(code).tokenize()
    preprocessor = preprocess(stream, evaluator.macros)
    parser = Parser(preprocessor)
    evaluator.node = parser.parse()
    evaluator.macros.update(parser.macros)
    return evaluator.visit() or None


try:
    while (command := input('JoLang >>> ')).lower() not in ('quit', 'exit'):
        res = main(command)
        if res is not None:
            print(res)
except KeyboardInterrupt:
    pass
