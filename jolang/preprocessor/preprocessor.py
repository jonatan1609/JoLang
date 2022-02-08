import typing
from ..tokenizer import tokens


def preprocess(stream: typing.Iterator[tokens.Token], macros=None):
    # Macro: '%macro' Identifier {Statement}
    if not macros:
        macros = {}
    copy = list(stream)
    stream = iter(copy.copy())
    c = 0
    for idx, token in enumerate(stream, 0):
        if isinstance(token, tokens.Modulo) and isinstance(copy[idx + c + bool(c) - 1], tokens.Newline):
            try:
                macro = next(stream)
                c += 1
                if macro.content == "macro":
                    replace, replace_with = next(stream), []
                    c += 1
                    assert isinstance(replace, tokens.Identifier), "A macro replace must be an identifier!"
                    while not isinstance(tok := next(stream, tokens.Newline), tokens.Newline):
                        c += 1
                        replace_with.append(tok)
                    macros[replace.name, replace.content] = replace_with
                else:
                    raise SyntaxError(f"Couldn't process a preprocessor command at line {token.line}") from None
            except StopIteration:
                try:
                    macro
                    replace
                except UnboundLocalError:
                    raise SyntaxError(f"Couldn't process a preprocessor command at line {token.line}") from None
        else:
            if (macro := macros.get((token.name, token.content))) is not None:
                yield from macro
            else:
                yield token
    yield macros
