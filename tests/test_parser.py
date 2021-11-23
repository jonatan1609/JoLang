from unittest import TestCase
from jolang.parser import Parser, ast
from jolang.tokenizer import Tokenizer
from jolang.preprocessor import preprocess


class TestParser(TestCase):
    tests_pass = {
        "func a(){for(;;){if(x){x}}}": ast.Body(statements=[ast.Function(name=ast.Name(argument='a'), params=ast.Arguments(items=[]), body=[ast.For(parts=[ast.Node(argument=None), ast.Node(argument=None), ast.Node(argument=None)], body=[ast.If(condition=ast.Name(argument='x'), body=[ast.Name(argument='x')], elifs=[], else_block=None)])])]),
        "for(1;a=b;){continue\nbreak\nif(x){~y}}": ast.Body(statements=[ast.For(parts=[ast.Number(argument=1), ast.Assignment(name=ast.Name(argument='a'), op=ast.Assign(), content=ast.Name(argument='b')), ast.Node(argument=None)], body=[ast.Continue(argument=None), ast.Break(argument=None), ast.If(condition=ast.Name(argument='x'), body=[ast.UnaryTilde(argument=ast.Name(argument='y'))], elifs=[], else_block=None)])]),
        "a=b<(c=k)": ast.Body(statements=[ast.Assignment(name=ast.Name(argument='a'), op=ast.Assign(), content=ast.Compare(left=ast.Name(argument='b'), op=ast.LesserThan(), right=ast.Assignment(name=ast.Name(argument='c'), op=ast.Assign(), content=ast.Name(argument='k'))))]),
        "a=b=c=d": ast.Body(statements=[ast.Assignment(name=ast.Name(argument='a'), op=ast.Assign(), content=ast.Assignment(name=ast.Name(argument='b'), op=ast.Assign(), content=ast.Assignment(name=ast.Name(argument='c'), op=ast.Assign(), content=ast.Name(argument='d'))))]),
        "1<2>3<=4>=5": ast.Body(statements=[ast.Compare(left=ast.Compare(left=ast.Compare(left=ast.Compare(left=ast.Number(argument=1), op=ast.LesserThan(), right=ast.Number(argument=2)), op=ast.GreaterThan(), right=ast.Number(argument=3)), op=ast.LessEqual(), right=ast.Number(argument=4)), op=ast.GreatEqual(), right=ast.Number(argument=5))]),
        "b - 1": ast.Body(statements=[ast.BinaryNode(left=ast.Name(argument='b'), op=ast.Subtract(), right=ast.Number(argument=1))]),
        "b += 1": ast.Body(statements=[ast.Assignment(name=ast.Name(argument='b'), op=ast.InplaceAdd(), content=ast.Number(argument=1))]),
        "~~b---1": ast.Body(statements=[ast.BinaryNode(left=ast.UnaryTilde(argument=ast.UnaryTilde(argument=ast.Name(argument='b'))), op=ast.Subtract(), right=ast.UnarySubtract(argument=ast.UnarySubtract(argument=ast.Number(argument=1))))]),
        "-b(2, 4, 5) + c(3,4, 4)": ast.Body(statements=[ast.BinaryNode(left=ast.UnarySubtract(argument=ast.Call(name=ast.Name(argument='b'), args=ast.Arguments(items=[ast.Number(argument=2), ast.Number(argument=4), ast.Number(argument=5)]))), op=ast.Add(), right=ast.Call(name=ast.Name(argument='c'), args=ast.Arguments(items=[ast.Number(argument=3), ast.Number(argument=4), ast.Number(argument=4)])))]),
        "0xcafe+0o567+0b100": ast.Body(statements=[ast.BinaryNode(left=ast.BinaryNode(left=ast.Number(argument=51966), op=ast.Add(), right=ast.Number(argument=375)), op=ast.Add(), right=ast.Number(argument=4))]),
        "if(x){if(1){}}elif(y){2}else{3}": ast.Body(statements=[ast.If(condition=ast.Name(argument='x'), body=[ast.If(condition=ast.Number(argument=1), body=[], elifs=[], else_block=None)], elifs=[ast.If(condition=ast.Name(argument='y'), body=[ast.Number(argument=2)], elifs=[], else_block=[ast.Number(argument=3)])], else_block=None)]),
        "%macro name 'xyz'\nprint(name)": ast.Body(statements=[ast.Call(name=ast.Name(argument='print'), args=ast.Arguments(items=[ast.String(argument='xyz')]))])
    }
    tests_fail = ["%macr", "-", "2-", "2=", "=s", "2+", "a=2=g", "func(){}", "if(){}", "continue", "return", "l&", "@", "{}", "a+a=b", "t>>", "'", '"', '*', "for(;){}", "for{}", "k l", "if(){}", "1 l", "l !r"]

    def test_parser_pass(self):
        for test, expect in self.tests_pass.items():
            t = Parser(preprocess(Tokenizer(test).tokenize())).parse()
            self.assertEqual(t, expect)

    def test_parser_fail(self):
        for test in self.tests_fail:
            self.assertRaises(SyntaxError, lambda: Parser(preprocess(Tokenizer(test).tokenize())).parse())
