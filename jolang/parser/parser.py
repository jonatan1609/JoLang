import typing
from .keywords import keywords
from ..tokenizer.tokens import Identifier, Token
from ..tokenizer import tokens
from . import ast


Keyword = Token("KEYWORD")


class Parser:
    def __init__(self, stream: typing.Iterable[Token]):
        self.macros: typing.Dict[typing.Tuple[str, str], typing.List[tokens.Token]] = {}
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
        elif self.accept(tokens.Identifier):  # Identifier: (LowerCase | UpperCase | '_') {Digit} {Identifier}
            if self.current_token.content in ("jomama", "yomama"):
                raise RuntimeError("Ayo! you found an easter egg")
            return ast.Constant(self.current_token.content)

    def parse_atom(self):
        # Atom: ({'~'|'-'|'+'|'!'} Atom) | '(' [LogicalOrExpr] ')' | Literal | (Literal '(' Args ')')
        if self.accept(tokens.LeftBracket):
            typ = self.parse_logical_or()
            if not self.accept(tokens.RightBracket):
                if not self.next_token:
                    self.next_token = self.current_token
                self.throw(f"Expected a ']', got {self.next_token.name}")
            else:
                obj = self.parse_logical_or()
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
                node = self.parse_logical_or()
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

    def parse_comp_op(self):
        # CompOp: '==' | '!=' | '<=' | '>=' | '<' | '>'
        table = {
            tokens.IsEqual: ast.Equals,
            tokens.NotEqual: ast.NotEqual,
            tokens.LessEqual: ast.LessEqual,
            tokens.GreatEqual: ast.GreatEqual,
            tokens.LesserThan: ast.LesserThan,
            tokens.GreaterThan: ast.GreaterThan
        }
        for i in (
            tokens.IsEqual, tokens.NotEqual,
            tokens.LessEqual, tokens.GreatEqual,
            tokens.LesserThan, tokens.GreaterThan,
        ):
            if self.accept(i):
                return table[i]

    def parse_comp(self):
        # CompExpr: BinaryOrExpr {CompOp BinaryOrExpr}
        node = self.parse_binary_or()
        while op := self.parse_comp_op():
            node = ast.Compare(node, op(), self.parse_binary_or())
        return node

    def parse_binary_or(self):
        # BinaryOrExpr: BinaryXorExpr {'||' BinaryXorExpr}
        node = self.parse_binary_xor()
        while self.accept(tokens.BinOr):
            node = ast.BinaryNode(node, ast.Or(), self.parse_binary_xor())
        return node

    def parse_binary_xor(self):
        # BinaryXorExpr: BinaryAndExpr {'^' BinaryAndExpr}
        node = self.parse_binary_and()
        while self.accept(tokens.Xor):
            node = ast.BinaryNode(node, ast.Xor(), self.parse_binary_and())
        return node

    def parse_binary_and(self):
        # BinaryAndExpr: ShiftExpr {'&&' ShiftExpr}
        node = self.parse_shift_expr()
        while self.accept(tokens.BinAnd):
            node = ast.BinaryNode(node, ast.And(), self.parse_shift_expr())
        return node

    def parse_shift_expr(self):
        # ShiftExpr: Expr {('<<' | '>>') Expr}
        node = self.parse_expr()
        while True:
            if self.accept(tokens.RightShift):
                node = ast.BinaryNode(node, ast.RightShift(), self.parse_expr())
            elif self.accept(tokens.LeftShift):
                node = ast.BinaryNode(node, ast.RightShift(), self.parse_expr())
            else:
                break
        return node

    def parse_logical_and(self):
        # LogicalOrExpr: LogicalXorExpr '||' LogicalXorExpr {'||' LogicalXorExpr}
        node = self.parse_comp()
        while self.accept(tokens.LogicAnd):
            node = ast.BinaryNode(node, ast.LogicAnd(), self.parse_comp())
        return node

    def parse_logical_or(self):
        # LogicalOrExpr: LogicalXorExpr '||' LogicalXorExpr {'||' LogicalXorExpr}
        node = self.parse_logical_and()
        while self.accept(tokens.LogicOr):
            node = ast.BinaryNode(node, ast.LogicOr(), self.parse_logical_and())
        return node

    def parse_args(self):
        # Args: Atom {',' Atom}
        args = [self.parse_logical_or()]
        while self.accept(tokens.Comma):
            args.append(self.parse_logical_or())
        return ast.Arguments(args)

    def parse_term(self):
        # Term: Atom {'*'|'/'|'%' Atom}
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
        # Expr: Term {'+'|'-' Term}
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
                expr = self.parse_logical_or()
                return ast.Assignment(name, expr)
            else:
                if not self.next_token:
                    self.next_token = self.current_token
                self.throw(f"Expected '=', got {self.next_token.name}")
        else:
            if not self.next_token:
                self.next_token = self.current_token
            self.throw(f"Expected an identifier, got {self.next_token.name}")

    def parse_if(self):
        pass

    def parse(self):
        body = ast.Body([])
        while not self.is_eof():
            if self.accept(tokens.Newline):
                pass
            if self.accept(Keyword):
                if self.current_token.content == "var":
                    node = self.parse_assignment()
                else:
                    self.throw(f"Expected 'var', got {self.current_token.name}")
            else:
                node = self.parse_logical_or()
            body.statements.append(node)
        return body
