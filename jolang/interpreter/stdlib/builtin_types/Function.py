from dataclasses import dataclass, field
from .object import Object
from .operator import Operator


@dataclass
class Function(Object):
    __post_init__ = Object.__init__
    name: str
    parameters: list = field(default_factory=list)
    body: list = field(default_factory=list)
    py_bind: ... = None
    restype: ... = None
    scope: ... = None

    @Operator("Call", compatible=["Function"])
    def call(self, *args):
        pass

