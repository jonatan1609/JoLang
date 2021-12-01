import typing


class Error:
    def __init__(self, p, current_tok, next_token):
        self.current_tok = current_tok
        self.next_token = next_token
        if not next_token:
            self.next_token = p.next_token = current_tok

    def __call__(self, message: typing.Optional[str]):
        if message:
            message += " at "
        else:
            message = ""
        raise SyntaxError(message + f"line {self.current_tok.line} column {self.next_token.col}")
