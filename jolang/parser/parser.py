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

    def parse_literal(self):
        # Literal: Digit | String | Identifier
        if self.accept(tokens.Integer):  # Digit: '0'|'1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9'
            return ast.Number(int(self.current_token.content))
        elif self.accept(tokens.String):  # String: ('"' {char} '"') | ("'" {char} "'")
            return ast.String(self.current_token.content)
        elif self.accept(tokens.Identifier):  # Identifier: (LowerCase | UpperCase | '_') Digit* Identifier*
            if self.current_token.content in ("jomama", "yomama"):
                raise RuntimeError("Ayo! you found an easter egg")
            return ast.Constant(self.current_token.content)

    def parse_atom(self):
        # Atom: ({'~'|'-'|'+'|'!'} Atom) | '(' [Expr] ')' | Literal | FuncCall | '[' Expr ']' Expr
        if self.accept(tokens.LeftBracket):
            typ = self.parse_expr()
            if not self.accept(tokens.RightBracket):
                if not self.next_token:
                    self.next_token = self.current_token
                self.throw(f"Expected a ']', got {self.next_token.name}")
            else:
                obj = self.parse_expr()
            node = ast.Cast(obj, typ)
        elif self.accept(tokens.UnaryTilde):
            node = ast.UnaryTilde(self.parse_atom())
        elif self.accept(tokens.LogicNot):
            node = ast.UnaryLogicalNot(self.parse_atom())
        elif self.accept(tokens.Add):
            node = ast.UnaryAdd(self.parse_atom())
        elif self.accept(tokens.Subtract):
            node = ast.UnarySubtract(self.parse_atom())
        elif literal := self.parse_literal():
            node = literal
        elif self.accept(tokens.LeftParen):
            if self.accept(tokens.RightParen):
                node = ast.Node(None)
            else:
                node = self.parse_expr()
                if not self.accept(tokens.RightParen):
                    self.throw(f"Parenthesis were not closed at line {self.current_token.line}")
        else:
            if not self.next_token:
                self.next_token = self.current_token
            self.throw(f"Expected an expression, got {self.next_token.name}.")
        while self.accept(tokens.LeftParen):
            if self.accept(tokens.RightParen):
                node = ast.Call(node, ast.Arguments([]))
            else:
                args = self.parse_args()
                if not self.accept(tokens.RightParen):
                    raise SyntaxError(f"Parenthesis were not closed at line {self.current_token.line}")
                node = ast.Call(node, args)
        return node

    def parse_args(self):
        # Args: Atom {',' Atom}
        args = [self.parse_expr()]
        while self.accept(tokens.Comma):
            args.append(self.parse_expr())
        return ast.Arguments(args)

    def parse_term(self):
        # Term: Atom('*'|'/'|'%' Atom)*
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

    def parse_assignment(self):
        # Assignment: 'var' Identifier '=' Expr
        if self.accept(tokens.Identifier):
            name = ast.Constant(argument=self.current_token.content)
            if self.accept(tokens.Equals):
                expr = self.parse_expr()
                return ast.Assignment(name, expr)
            else:
                if not self.next_token:
                    self.next_token = self.current_token
                self.throw(f"Expected '=', got {self.next_token.name}")
        else:
            if not self.next_token:
                self.next_token = self.current_token
            self.throw(f"Expected an identifier, got {self.next_token.name}")

    def parse_cast(self):
        pass

    def parse(self):
        body = ast.Body([])
        while not self.is_eof():
            if self.accept(tokens.Newline):
                pass
            if self.accept(Keyword):
                node = self.parse_assignment()
            else:
                node = self.parse_expr()
            body.statements.append(node)
        return body
