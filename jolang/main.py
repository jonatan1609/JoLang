from .tokenizer import Tokenizer, tokens_generator, tokens
from .preprocessor import preprocess
from .parser import Parser
from .interpreter import Interpreter, file


def untokenize(stream):
    for i in stream:
        yield getattr(tokens, tokens_generator.uppercase_to_pascal_case(i.name)).value or i.content


def main(code: str):
    stream = Tokenizer(code).tokenize()
    interpreter = Interpreter(file.File(code, "shell", Parser(preprocess(stream)).parse()))
    return interpreter.eval()

