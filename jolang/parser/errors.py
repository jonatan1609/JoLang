class Error:
    def __init__(self, current_tok, next_token):
        self.current_tok = current_tok
        self.next_token = next_token

    def __enter__(self):
        if not self.next_token:
            self.next_token = self.current_tok
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, message: str):
        raise SyntaxError(message + f" at line {self.next_token.line} column {self.next_token.col}")
