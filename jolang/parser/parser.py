import typing
from .keywords import keywords
from ..tokenizer.tokens import Identifier, Token
from ..tokenizer import tokens
from . import ast


Keyword = Token("KEYWORD")


class Parser:
    def __init__(self, stream: typing.Iterable[Token]):
        self.macros = {}
        self.tokens_stream = self.cast_identifier_to_keyword(stream)
        self.current_token: typing.Optional[Token] = None
        self.next_token: typing.Optional[Token] = None
        self.advance()

    def advance(self) -> None:
        self.current_token, self.next_token = self.next_token, next(self.tokens_stream, None)

    def is_eof(self) -> bool:
        return not self.next_token

    def cast_identifier_to_keyword(self, stream: typing.Iterable[Token]) -> typing.Generator[Token, None, None]:
        for token in stream:
            if isinstance(token, dict):
                self.macros = token
                continue
            if token.name == Identifier.name and token.content in keywords:
                yield Keyword.set_content(token.line, token.col, token.content)
            else:
                yield token

    def accept(self, token: Token):
        if self.next_token and isinstance(self.next_token, token):
            self.advance()
            return True
        return False

    def throw(self, message: str):
        raise SyntaxError(message + f" at line {self.next_token.line} column {self.next_token.col}")

    def parse_atom(self):
        # Expr | ({'~'|'-'|'+'|'!'}* Atom)
        if self.accept(tokens.Integer):
            return ast.Number(int(self.current_token.content))
        elif self.accept(tokens.String):
            return ast.String(self.current_token.content)
        elif self.accept(tokens.Identifier):
            return ast.Constant(self.current_token.content)
        elif self.accept(tokens.UnaryTilde):
            return ast.UnaryTilde(self.parse_atom())
        elif self.accept(tokens.LogicNot):
            return ast.UnaryLogicalNot(self.parse_atom())
        elif self.accept(tokens.Add):
            return ast.UnaryAdd(self.parse_atom())
        elif self.accept(tokens.Subtract):
            return ast.UnarySubtract(self.parse_atom())
        elif self.accept(tokens.LeftParen):
            expr = self.parse_expr()
            if not self.accept(tokens.RightParen):
                raise SyntaxError(f"Parenthesis were not closed at line {self.current_token.line}")
            return expr
        else:
            if not self.next_token:
                self.next_token = self.current_token
            self.throw(f"Expected ~,-,+,!,expression got {self.next_token.name}.")

    def parse_term(self):
        # Term: Atom('*'|'/' Term)*
        node = self.parse_atom()
        while True:
            if self.accept(tokens.Multiply):
                node = ast.BinaryNode(left=node, op=ast.Multiply(), right=self.parse_atom())
            elif self.accept(tokens.Divide):
                node = ast.BinaryNode(left=node, op=ast.Divide(), right=self.parse_atom())
            elif self.accept(tokens.Modulo):
                node = ast.BinaryNode(left=node, op=ast.Modulo(), right=self.parse_atom())
            else:
                break
        return node

    def parse_expr(self):
        # Expr: Term('+'|'-' Term)*
        node = self.parse_term()
        while True:
            if self.accept(tokens.Add):
                node = ast.BinaryNode(left=node, op=ast.Add(), right=self.parse_term())
            elif self.accept(tokens.Subtract):
                node = ast.BinaryNode(left=node, op=ast.Subtract(), right=self.parse_term())
            else:
                break
        return node

    def parse(self):
        body = ast.Body([])
        while not self.is_eof():
            if self.accept(tokens.Newline):
                continue
            body.statements.append(self.parse_expr())
        return body
