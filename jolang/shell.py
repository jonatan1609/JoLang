import re

from jolang.tokenizer import Tokenizer
from jolang.preprocessor import preprocess
from jolang.parser import Parser, ast


class Evaluate:
    PATTERN = re.compile(r'(?=[A-Z])')

    def __init__(self, node: ast.Body):
        self.node = node

    @staticmethod
    def pascal_case_to_snake_case(string: str):
        return "_".join(x.lower() for x in Evaluate.PATTERN.split(string) if x)

    @staticmethod
    def visit_number(node: ast.Number):
        return node.argument

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

    def visit(self):
        if self.node.statements:
            return self._visit(self.node.statements[0])
        return ''


def main(code: str):
    stream = Tokenizer(code).tokenize()
    return Evaluate(Parser(preprocess(stream)).parse()).visit()


try:
    while (command := input('JoLang >>> ')).lower() not in ('quit', 'exit'):
        print(main(command))
except KeyboardInterrupt:
    pass
