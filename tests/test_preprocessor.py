from unittest import TestCase
from jolang.preprocessor import preprocess
from jolang.tokenizer import Tokenizer, tokens


class TestPreprocessor(TestCase):
    tests_pass = {
        "%macro a": [{('IDENTIFIER', 'a'): []}],
        "%macro a 1": [{('IDENTIFIER', 'a'): [tokens.Integer]}],
        "%macro a 2 + a": [{('IDENTIFIER', 'a'): [tokens.Integer, tokens.Add, tokens.Identifier]}]
    }

    tests_fail = ["%", "%macro 0", "%macro", "%macro", "%macro ~ []"]

    def test_pass(self):
        for test, expect in self.tests_pass.items():
            p = list(preprocess(Tokenizer(test).tokenize()))
            self.assertEqual(p[0].keys(), expect[0].keys())
            pv, = list(p[0].values())
            ev, = list(expect[0].values())
            for i in range(len(ev)):
                self.assertIsInstance(pv[i], ev[i])

    def test_fail(self):
        for test in self.tests_fail:
            self.assertRaises((AssertionError, SyntaxError), lambda: list(preprocess(Tokenizer(test).tokenize())))