import re

from jolang.tokenizer import Tokenizer
from jolang.preprocessor import preprocess
from jolang.parser import Parser, ast


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

    def _visit(self, node):
        method = 'visit_' + self.pascal_case_to_snake_case(node.__class__.__name__)
        method = getattr(self, method)
        return method(node)

    @staticmethod
    def visit_string(node):
        return node.argument

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
    return evaluator.visit()


try:
    while (command := input('JoLang >>> ')).lower() not in ('quit', 'exit'):
        res = main(command)
        if res:
            print(res)
except KeyboardInterrupt:
    pass
