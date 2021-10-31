import typing
from ..tokenizer import tokens


def preprocess(stream: typing.Iterator[tokens.Token]):
    macros = {}
    for token in stream:
        if isinstance(token, tokens.Modulo) and not token.col:
            try:
                macro = next(stream)
                if macro.content == "macro":
                    replace, replace_with = next(stream), []
                    while not isinstance(tok := next(stream), tokens.Newline):
                        replace_with.append(tok)
                    macros[replace.name, replace.content] = replace_with
            except StopIteration:
                break
        else:
            if (macro := macros.get((token.name, token.content))) is not None:
                yield from macro
            else:
                yield token
