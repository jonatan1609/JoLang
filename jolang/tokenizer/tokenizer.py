import string
import re
from . import tokens

TokenStream = iter


class Tokenizer:
    INTEGER_PATTERN = re.compile(r"\d+")
    FLOAT_PATTERN = re.compile(r"\d+\.?\d*")
    HEX_PATTERN = re.compile(r"0x[\da-f]+", re.IGNORECASE)
    OCTAL_PATTERN = re.compile(r"0o[0-7]+", re.IGNORECASE)

    map_re_to_tokens = {
        INTEGER_PATTERN: lambda content: tokens.Integer.set_content(content),
        FLOAT_PATTERN: lambda content: tokens.Float.set_content(content),
        HEX_PATTERN: lambda content: tokens.Integer.set_content(int(content, 16)),
        OCTAL_PATTERN: lambda content: tokens.Integer.set_content(int(content, 8))
    }

    def __init__(self, stream: str):
        self.tokens = TokenStream(stream)
        self.current_token = None
        self.advance()

    def advance(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None
        return self.current_token

    def is_eof(self):
        return not self.current_token

    def tokenize_string(self):
        char = self.current_token
        self.advance()
        while self.current_token != char:
            yield self.current_token
            self.advance()
            if self.is_eof():
                raise SyntaxError("String was never closed")
        self.advance()

    def tokenize_number(self):
        number = ""
        while not self.is_eof() and self.current_token in string.ascii_letters + string.digits + '.':
            number += self.current_token
            self.advance()
        for regex in (
                self.INTEGER_PATTERN,
                self.FLOAT_PATTERN,
                self.OCTAL_PATTERN,
                self.HEX_PATTERN
        ):
            if regex.fullmatch(number):
                return self.map_re_to_tokens[regex](number)
        raise SyntaxError(f"Couldn't tokenize the number {number!r}")

    def tokenize_identifier(self):
        while not self.is_eof() and self.current_token in string.ascii_letters + string.digits + "_":
            yield self.current_token
            self.advance()

    def _get_op_one_char(self):
        tok = tokens.one_char(self.current_token)
        if tok == tokens.Comment:
            while not self.is_eof() and self.current_token != '\n':
                self.advance()
        return tok

    def _get_op_two_chars(self, first: tokens.Token):
        if first.value and self.current_token and (tok := tokens.two_chars(first.value + self.current_token)):
            return tok

    def _get_op_three_chars(self, first: tokens.Token):
        if first.value and self.current_token and (tok := tokens.three_chars(first.value + self.current_token)):
            return tok

    def tokenize_op(self):
        three_tok = two_tok = None

        if tok := self._get_op_one_char():
            self.advance()
            if self.current_token and (two_tok := self._get_op_two_chars(tok)):
                self.advance()
                if self.current_token and (three_tok := self._get_op_three_chars(two_tok)):
                    self.advance()

        return three_tok or two_tok or tok

    def tokenize(self):
        while not self.is_eof():
            if self.current_token in ['\'', '"']:
                yield tokens.String.set_content("".join(self.tokenize_string()))
            elif self.current_token in string.whitespace:
                self.advance()
            elif self.current_token in string.digits:
                yield self.tokenize_number()
            elif self.current_token in string.ascii_letters + "_":
                yield tokens.Identifier.set_content("".join(self.tokenize_identifier()))
            else:
                if op := self.tokenize_op():
                    if op == tokens.Comment:
                        continue
                    yield op
                else:
                    raise SyntaxError(f"Invalid Syntax {self.current_token!r}")