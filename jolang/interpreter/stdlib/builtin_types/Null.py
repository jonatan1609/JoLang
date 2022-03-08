from .object import Object


class Null(Object):
    def __init__(self, *_):
        super().__init__()
        self._obj = "null"
