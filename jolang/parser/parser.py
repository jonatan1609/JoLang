import typing
from .keywords import keywords
from ..tokenizer.tokens import Identifier, Token
from ..tokenizer import tokens
from . import ast, errors


Keyword = Token("KEYWORD")


class Parser:
    comp_op_table = {
            tokens.IsEqual: ast.Equals,
            tokens.NotEqual: ast.NotEqual,
            tokens.LessEqual: ast.LessEqual,
            tokens.GreatEqual: ast.GreatEqual,
            tokens.LesserThan: ast.LesserThan,
            tokens.GreaterThan: ast.GreaterThan
    }
    inplace_op_table = {
        tokens.Equals: ast.Assign,
        tokens.InplaceAdd: ast.InplaceAdd,
        tokens.InplaceSubtract: ast.InplaceSubtract,
        tokens.InplaceModulo: ast.InplaceModulo,
        tokens.InplaceMultiply: ast.InplaceMultiply,
        tokens.InplaceDivide: ast.InplaceDivide,
        tokens.InplaceRightShift: ast.InplaceRightShift,
        tokens.InplaceLeftShift: ast.InplaceLeftShift,
        tokens.InplaceBinOr: ast.InplaceBinOr,
        tokens.InplaceBinAnd: ast.InplaceBinAnd,
        tokens.InplaceXor: ast.InplaceXor
    }

    def __init__(self, stream: typing.Iterable[Token]):
        self.macros: typing.Dict[typing.Tuple[str, str], typing.List[tokens.Token]] = {}
        self.tokens_stream = self.cast_identifier_to_keyword(stream)
        self.current_token: typing.Optional[Token] = None
        self.next_token: typing.Optional[Token] = None
        self.advance()

    def advance(self) -> None:
        self.current_token, self.next_token = self.next_token, next(self.tokens_stream, None)

    def push_token_back(self):
        self.tokens_stream = iter([self.current_token, self.next_token] + list(self.tokens_stream))
        self.advance()

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

    @property
    def throw(self):
        return errors.Error(self, self.current_token, self.next_token)

    def parse_literal(self):
        # Literal: Digit | String | Identifier
        if self.accept(tokens.Integer):  # Digit: '0'|'1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9'
            return ast.Integer(self.current_token.line, self.current_token.col, int(self.current_token.content))
        elif self.accept(tokens.String):  # String: ('"' {char} '"') | ("'" {char} "'")
            return ast.String(self.current_token.line, self.current_token.col, self.current_token.content)
        elif self.accept(tokens.Identifier):  # Identifier: (LowerCase | UpperCase | '_') {Digit} {Identifier}
            return ast.Name(self.current_token.line, self.current_token.col, self.current_token.content)

    def parse_atom(self):
        node = None
        unary_op = True
        # Atom: ({'~'|'-'|'+'|'!'} Atom) | '(' [LogicalOrExpr] ')' | Literal | (Literal '(' [Args] ')')
        if self.accept(tokens.UnaryTilde):
            node = ast.UnaryTilde(self.current_token.line, self.current_token.col, self.parse_atom())
        elif self.accept(tokens.LogicNot):
            node = ast.UnaryLogicalNot(self.current_token.line, self.current_token.col, self.parse_atom())
        elif self.accept(tokens.Add):
            node = ast.UnaryAdd(self.current_token.line, self.current_token.col, self.parse_atom())
        elif self.accept(tokens.Subtract):
            node = ast.UnarySubtract(self.current_token.line, self.current_token.col, self.parse_atom())
        else:
            unary_op = False
        if not unary_op:
            if literal := self.parse_literal():
                node = literal
            elif self.accept(tokens.LeftParen):
                if self.accept(tokens.RightParen):
                    node = ast.Node(self.current_token.line, self.current_token.col-2)
                else:
                    node = self.parse_assignment()
                    if not self.accept(tokens.RightParen):
                        self.throw(f"Parenthesis were not closed")
            while self.accept(tokens.LeftParen):
                if self.accept(tokens.RightParen):
                    node = ast.Call(self.current_token.line, self.current_token.col - 1, node, ast.Arguments(self.current_token.line, self.current_token.col, []))
                else:
                    line, col = self.current_token.line, self.current_token.col
                    args = self.parse_args()
                    if not self.accept(tokens.RightParen):
                        raise SyntaxError(f"Parenthesis were not closed at line {self.current_token.line}")
                    node = ast.Call(line, col, node, args)
        if unary_op and not node.argument:
            self.current_token.col += 1
            self.throw(None)
        return node

    def parse_comp_op(self):
        # CompOp: '==' | '!=' | '<=' | '>=' | '<' | '>'
        for i, l in (
                (tokens.IsEqual, 2), (tokens.NotEqual, 2),
                (tokens.LessEqual, 2), (tokens.GreatEqual, 2),
                (tokens.LesserThan, 1), (tokens.GreaterThan, 1),
        ):
            if self.accept(i):
                return self.comp_op_table[i], l

    def parse_comp(self):
        # CompExpr: BinaryOrExpr {CompOp BinaryOrExpr}
        node = self.parse_binary_or()
        while op := self.parse_comp_op():
            node = ast.Compare(self.current_token.line, self.current_token.col, node, op[0](self.current_token.line, self.current_token.col), self.parse_binary_or())
            if not node.right or not node.left:
                self.current_token.col += op[1]
                self.throw(None)
        return node

    def parse_binary_or(self):
        # BinaryOrExpr: BinaryXorExpr {'||' BinaryXorExpr}
        node = self.parse_binary_xor()
        while self.accept(tokens.BinOr):
            node = ast.BinaryNode(self.current_token.line, self.current_token.col, node, ast.Or(self.current_token.line, self.current_token.col), self.parse_binary_xor())
            if not node.right or not node.left:
                self.current_token.col += 1
                self.throw(None)
        return node

    def parse_binary_xor(self):
        # BinaryXorExpr: BinaryAndExpr {'^' BinaryAndExpr}
        node = self.parse_binary_and()
        while self.accept(tokens.Xor):
            node = ast.BinaryNode(self.current_token.line, self.current_token.col, node, ast.Xor(self.current_token.line, self.current_token.col), self.parse_binary_and())
            if not node.right or not node.left:
                self.current_token.col += 1
                self.throw(None)
        return node

    def parse_binary_and(self):
        # BinaryAndExpr: ShiftExpr {'&&' ShiftExpr}
        node = self.parse_shift_expr()
        while self.accept(tokens.BinAnd):
            node = ast.BinaryNode(self.current_token.line, self.current_token.col, node, ast.And(self.current_token.line, self.current_token.col), self.parse_shift_expr())
            if not node.right or not node.left:
                self.current_token.col += 1
                self.throw(None)
        return node

    def parse_shift_expr(self):
        # ShiftExpr: Expr {('<<' | '>>') Expr}
        node = self.parse_expr()
        while not self.is_eof():
            if self.accept(tokens.RightShift):
                node = ast.BinaryNode(self.current_token.line, self.current_token.col, node, ast.RightShift(self.current_token.line, self.current_token.col), self.parse_expr())
            elif self.accept(tokens.LeftShift):
                node = ast.BinaryNode(self.current_token.line, self.current_token.col, node, ast.RightShift(self.current_token.line, self.current_token.col), self.parse_expr())
            else:
                break
            if not node.right or not node.left:
                self.current_token.col += 2
                self.throw(None)
        return node

    def parse_return(self, *_):
        # 'return' Assignment
        return ast.Return(line=self.current_token.line, column=self.current_token.col, argument=self.parse_assignment())

    def parse_logical_and(self):
        # LogicalAndExpr: CompExpr {'||' CompExpr}
        node = self.parse_comp()
        while self.accept(tokens.LogicAnd):
            node = ast.BinaryNode(self.current_token.line, self.current_token.col, node, ast.LogicAnd(self.current_token.line, self.current_token.col), self.parse_comp())
            if not node.right or not node.left:
                self.current_token.col += 1
                self.throw(None)
        return node

    def parse_logical_or(self):
        # LogicalOrExpr: LogicalAndExpr {'||' LogicalAndExpr}
        node = self.parse_logical_and()
        while self.accept(tokens.LogicOr):
            node = ast.BinaryNode(self.current_token.line, self.current_token.col, node, ast.LogicOr(self.current_token.line, self.current_token.col), self.parse_logical_and())
            if not node.right or not node.left:
                self.current_token.col += 1
                self.throw(None)
        return node

    def parse_args(self):
        # Args: Atom {',' Atom}
        args = [self.parse_assignment()]
        while self.accept(tokens.Comma):
            args.append(self.parse_assignment())
        return ast.Arguments(self.current_token.line, self.current_token.col, args)

    def parse_term(self):
        # Term: Atom {'*'|'/'|'%' Atom}
        node = self.parse_atom()
        while not self.is_eof():
            if self.accept(tokens.Multiply):
                node = ast.BinaryNode(line=self.current_token.line, column=self.current_token.col,left=node, op=ast.Multiply(self.current_token.line, column=self.current_token.col), right=self.parse_atom())
            elif self.accept(tokens.Divide):
                node = ast.BinaryNode(line=self.current_token.line, column=self.current_token.col, left=node, op=ast.Divide(self.current_token.line, column=self.current_token.col), right=self.parse_atom())
            elif self.accept(tokens.Modulo):
                node = ast.BinaryNode(line=self.current_token.line, column=self.current_token.col,left=node, op=ast.Modulo(self.current_token.line, column=self.current_token.col), right=self.parse_atom())
            else:
                break
            if not node.right or not node.left:
                self.current_token.col += 1
                self.throw(None)
        return node

    def parse_expr(self):
        # Expr: Term {'+'|'-' Term}
        node = self.parse_term()
        while not self.is_eof():
            if self.accept(tokens.Add):
                node = ast.BinaryNode(self.current_token.line, self.current_token.col, left=node, op=ast.Add(self.current_token.line, self.current_token.col, ), right=self.parse_term())
            elif self.accept(tokens.Subtract):
                node = ast.BinaryNode(self.current_token.line, self.current_token.col, left=node, op=ast.Subtract(self.current_token.line, self.current_token.col, ), right=self.parse_term())
            else:
                break
            if not node.right or not node.left:
                self.current_token.col += 1
                self.throw(None)
        return node

    def parse_assignment(self):
        # Assignment: {Identifier '='} LogicalOrExpr
        asses = []
        while self.accept(tokens.Identifier):
            name = ast.Name(self.current_token.line, self.current_token.col, self.current_token.content)
            for i, l in (
                    (tokens.Equals, 1), (tokens.InplaceAdd, 2),
                    (tokens.InplaceSubtract, 2), (tokens.InplaceModulo, 2),
                    (tokens.InplaceMultiply, 2), (tokens.InplaceDivide, 2),
                    (tokens.InplaceRightShift, 2), (tokens.InplaceLeftShift, 2),
                    (tokens.InplaceBinOr, 2), (tokens.InplaceBinAnd, 2), (tokens.InplaceXor, 2)
            ):
                if self.accept(i):
                    asses.append(self.inplace_op_table[i](self.current_token.line, self.current_token.col))
                    asses.append(name)
                    break
            else:
                if isinstance(self.current_token, tokens.Identifier):
                    self.push_token_back()
                    break
            if not asses:
                self.push_token_back()
                break
        line = self.current_token.line
        node = self.parse_logical_or()
        while asses:
            if not node:
                self.current_token.col += l
                self.throw(None)

            node = ast.Assignment(line, self.current_token.col, asses.pop(), asses.pop(), node)
        return node

    def parse_params(self):
        # Params: Identifier {',' Identifier}
        params = ast.Arguments(self.current_token.line, self.current_token.col, [])
        while self.accept(tokens.Identifier):
            params.items.append(ast.Name(self.current_token.line, self.current_token.col, argument=self.current_token.content))
            if not self.accept(tokens.Comma):
                break
        return params

    def parse_func(self, keywords):
        for i in ('continue', 'break'):
            if i in keywords:
                del keywords[i]
        # Func: 'func' Identifier '(' [Params] ')' '{' FuncBlock '}'
        if self.accept(tokens.Identifier):
            name = ast.Name(self.current_token.line, self.current_token.col, argument=self.current_token.content)
            params = ast.Arguments(self.current_token.line, self.current_token.col, [])
            if self.accept(tokens.LeftParen):
                params = self.parse_params()
                if not self.accept(tokens.RightParen):
                    self.throw(f"Expected ')', got {self.next_token.name}")
                if self.accept(tokens.LeftBrace):
                    statements = self.parse_block(keywords={
                        **keywords,
                        "return": self.parse_return
                    })
                    if not self.accept(tokens.RightBrace):
                        self.throw(f"Expected '}}', got {self.next_token.name}")
                else:
                    self.throw(f"Expected '{{', got {self.next_token.name}")
            else:
                self.throw(f"Expected '(', got {self.next_token.name}")
            return ast.Function(self.current_token.line, self.current_token.col, name=name, params=params, body=statements)
        else:
            self.throw(f"Expected an identifier, got {self.next_token.name}")

    def parse_block(self, keywords=None):
        # Block: {Assignment | Func | IfStmt | WhileLoop | ForLoop | NEWLINE}
        statements = []
        if not keywords:
            keywords = {}
        keywords = {
            "if": self.parse_if_stmt,
            "func": self.parse_func,
            "for": self.parse_for_loop,
            "while": self.parse_while_loop,
            **keywords
        }
        while not self.is_eof():
            while self.accept(tokens.Newline):
                pass
            if self.accept(Keyword):
                if f := keywords.get(self.current_token.content):
                    statements.append(f(keywords))
                else:
                    self.throw("Did not expect a keyword.")
            elif assignment := self.parse_assignment():
                statements.append(assignment)
            elif isinstance((self.next_token or self.current_token), tokens.RightBrace):
                break
            else:
                break
            if (not isinstance(self.current_token, tokens.RightBrace)) and self.next_token and (not isinstance(self.next_token, tokens.RightBrace)) and (not self.accept(tokens.Newline)):
                if not isinstance(self.current_token, tokens.Newline):
                    self.throw(f"Expected a newline, got {self.next_token}")
        return statements

    def parse_if_stmt(self, keywords):
        # IfStmt: 'if' '(' Assignment ')' '{' Block '}'
        else_block = None
        if self.accept(tokens.LeftParen):
            stmt = self.parse_assignment()
            if not stmt:
                self.throw(f"Expected expression")
            if not self.accept(tokens.RightParen):
                self.throw(f"Expected ')', got {self.next_token.name}")
            while self.accept(tokens.Newline):
                pass
            if not self.accept(tokens.LeftBrace):
                self.throw(f"Expected '{{', got {self.next_token.name}")
            block = self.parse_block(keywords)
            if not self.accept(tokens.RightBrace):
                self.throw(f"Expected '}}', got {self.next_token.name}")
        else:
            self.throw(f"Expected '(', got {self.next_token.name}")
        elifs = []
        while self.accept(tokens.Newline):
            pass
        while not self.is_eof() and self.next_token.content == "elif":
            # ElifStmt: 'elif' '(' Assignment ')' '{' Block '}'
            self.advance()
            elifs.append(self.parse_if_stmt(keywords))
        while self.accept(tokens.Newline):
            pass
        if not self.is_eof() and self.next_token.content == "else":
            # ElseStmt: 'else' '{' Block '}'
            self.advance()
            if not self.accept(tokens.LeftBrace):
                self.throw(f"Expected '{{', got {self.next_token.name}")
            else_block = self.parse_block()
            if not self.accept(tokens.RightBrace):
                self.throw(f"Expected '}}', got {self.next_token.name}")
        return ast.If(self.current_token.line, self.current_token.col, condition=stmt, body=block, elifs=elifs, else_block=else_block)

    def parse_while_loop(self, keywords):
        # WhileLoop: 'while' '(' Assignment ')' '{' Block '}'
        if self.accept(tokens.LeftParen):
            stmt = self.parse_assignment()
            if not stmt:
                self.throw(f"Expected expression")
            if not self.accept(tokens.RightParen):
                self.throw(f"Expected ')', got {self.next_token.name}")
            if not self.accept(tokens.LeftBrace):
                self.throw(f"Expected '{{', got {self.next_token.name}")
            block = self.parse_block(keywords={
                **keywords,
                "continue": lambda *_: ast.Continue(line=self.current_token.line, column=self.current_token.col),
                "break": lambda *_: ast.Break(line=self.current_token.line, column=self.current_token.col)
            })
            if not self.accept(tokens.RightBrace):
                self.throw(f"Expected '}}', got {self.next_token.name}")
        else:
            self.throw(f"Expected '(', got {self.next_token.name}")
        return ast.While(self.current_token.line, self.current_token.col, stmt, block)

    def parse_for_loop(self, keywords):
        # ForLoop: 'for' '(' [Assignment] ';' [Assignment] ';' [Assignment] ')' '{' Block '}'
        parts = []
        if self.accept(tokens.LeftParen):
            for i in range(2):  # three parts in a for loop
                if self.accept(tokens.Semicolon):
                    parts.append(ast.Node(self.current_token.line, self.current_token.col, ))
                else:
                    parts.append(self.parse_assignment())
                    if not self.accept(tokens.Semicolon):
                        self.throw(f"Expected ';', got {self.next_token.name}")
            parts.append(self.parse_assignment() or ast.Node(self.current_token.line, self.current_token.col))
            if not self.accept(tokens.RightParen):
                self.throw(f"Expected ')', got {self.next_token.name}")
            if not self.accept(tokens.LeftBrace):
                self.throw(f"Expected '{{', got {self.next_token.name}")
            block = self.parse_block(keywords={
                **keywords,
                "continue": lambda *_: ast.Continue(line=self.current_token.line, column=self.current_token.col),
                "break": lambda *_: ast.Break(line=self.current_token.line, column=self.current_token.col)
            })
            if not self.accept(tokens.RightBrace):
                self.throw(f"Expected '}}', got {self.next_token.name}")
        else:
            self.throw(f"Expected '(', got {self.next_token.name}")
        return ast.For(self.current_token.line, self.current_token.col, parts, block)

    def parse(self):
        body = ast.Body(self.next_token.line, self.next_token.col, [])
        while not self.is_eof():
            node = self.parse_block()
            if self.next_token and not self.accept(tokens.Newline):
                self.throw(f"got {self.next_token.name}")
            body.statements = node
        return body
