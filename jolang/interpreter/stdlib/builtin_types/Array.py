from .object import Object
from .operator import Operator, Attribute
from .String import String
from .Integer import Integer
from .Null import Null



class Array(Object):
    def __init__(self, items):
        super().__init__()
        self._obj = items

    @Operator("Index", compatible=["Integer"])
    def index(self, start, stop, step):
        if start and not (stop or step):
            return self._obj[getattr(start, "_obj", None)]
        return Array(self._obj[getattr(start, "_obj", None):getattr(stop, "_obj", None):getattr(step, "_obj", None)])

    @Attribute("append")
    def append(self, item):
        if isinstance(item, str):
            item = String(item)
        elif item is None:
            item = Null()
        elif isinstance(item, int):
            item = Integer(item)
        elif isinstance(item, list):
            item = Array(item)
        self._obj.append(item)
