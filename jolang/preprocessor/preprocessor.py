import typing
from ..tokenizer import tokens


def preprocess(stream: typing.Iterator[tokens.Token], macros=None):
    # Macro: '%' Identifier Expr
    if not macros:
        macros = {}
    for token in stream:
        if isinstance(token, tokens.Modulo) and not token.col:
            try:
                macro = next(stream)
                if macro.content == "macro":
                    replace, replace_with = next(stream), []
                    assert isinstance(replace, tokens.Identifier), "A macro replace must be an identifier!"
                    while not isinstance(tok := next(stream, tokens.Newline), tokens.Newline):
                        replace_with.append(tok)
                    macros[replace.name, replace.content] = replace_with
                else:
                    raise SyntaxError(f"Couldn't process a macro at line {token.line}")
            except StopIteration:
                try:
                    macro
                    replace
                except UnboundLocalError:
                    raise SyntaxError(f"Couldn't process a macro at line {token.line}")
        else:
            if (macro := macros.get((token.name, token.content))) is not None:
                yield from macro
            else:
                yield token
    yield macros
