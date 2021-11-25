from unittest import TestCase
from jolang.tokenizer import Tokenizer, tokens


class TestTokenizer(TestCase):
    tests_pass = {
        "+": [tokens.Add],
        "-": [tokens.Subtract],
        ">>": [tokens.RightShift],
        ">>=": [tokens.InplaceRightShift],
        "|": [tokens.BinOr],
        "||": [tokens.LogicOr],
        "abc a0 01": [tokens.Identifier, tokens.Identifier, tokens.Integer],
        "0x222 0o222 2.2": [tokens.Integer, tokens.Integer, tokens.Float],
        "func a(){return a % 2 - 1 == 2}": [tokens.Identifier, tokens.Identifier, tokens.LeftParen, tokens.RightParen, tokens.LeftBrace, tokens.Identifier, tokens.Identifier, tokens.Modulo, tokens.Integer, tokens.Subtract, tokens.Integer, tokens.IsEqual, tokens.Integer, tokens.RightBrace],
        "$ abc": [],
        "a $abc \n a": [tokens.Identifier, tokens.Identifier]
    }

    tests_fail = ["0a", "0.a", "0o8", "@"]

    def test_tokenizer_pass(self):
        for test, expect in self.tests_pass.items():
            t = list(Tokenizer(test).tokenize())
            self.assertTrue(len(t) == len(expect), f"Length of tokens isn't {len(expect)}")
            for i in range(len(expect)):
                self.assertIsInstance(t[i], expect[i])

    def test_tokenizer_fail(self):
        for test in self.tests_fail:
            self.assertRaises(SyntaxError, lambda: list(Tokenizer(test).tokenize()))
