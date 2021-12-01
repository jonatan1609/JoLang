import typing


class StackCall:
    def __init__(self, file: str, line: int, column: int, scope: str, statement: str):
        self.file = file
        self.line = line
        self.column = column
        self.scope = scope
        self.statement = statement

    def repr(self):
        return f"File {self.file!r}, line {self.line} column {self.column} in {self.scope}:\n\t\t{self.statement}\n\t\t{'^':>{self.column+1}}"


class Error:
    def __init__(self, message: str = None, stack: typing.List[StackCall] = None):
        if not message:
            message = ""
        self.message = message
        self.stack = stack or []

    @property
    def get_error_class(self):
        return self.__class__.__name__

    def throw(self):
        print("Traceback (old-to-recent calls):")
        for call in self.stack:
            print("\t", call.repr())
        print(self.get_error_class + ":", self.message)
        exit()


class InterpretationError(Error):
    pass


class NameError(Error):
    pass


class OperatorError(Error):
    pass


class RuntimeError(Error):
    pass
