class File:
    def __init__(self, code: str, name: str, ast):
        self.lines = code.splitlines()
        self.name = name
        self.ast = ast

    def line(self, number):
        return self.lines[number]
