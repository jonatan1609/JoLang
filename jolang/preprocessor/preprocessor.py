import typing
from ..tokenizer import tokens


def preprocess(stream: typing.Iterator[tokens.Token]):
    macros = {}
    for token in stream:
        if isinstance(token, tokens.Modulo) and not token.col:
            try:
                macro = next(stream)
                if macro.content == "macro":
                    replace, replace_with = next(stream), [next(stream)]
                    if isinstance(replace_with[0], tokens.LeftParen):
                        replace_with.pop()
                        while not isinstance(tok := next(stream), tokens.RightParen):
                            replace_with.append(tok)
                    newline = next(stream)
                    if not isinstance(newline, tokens.Newline):
                        raise SyntaxError("A macro should be end with a newline [{}:{}]".format(macro.line, macro.col - 1))
                    macros[replace.name, replace.content] = replace_with
            except StopIteration:
                raise SyntaxError("A macro was never closed [line {}]".format(macro.line)) from None
        else:
            if macro := macros.get((token.name, token.content)):
                yield from macro
            else:
                yield token
