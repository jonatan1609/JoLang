from ..builtin_types.Function import Function
from ..builtin_types.Null import Null
from ..builtin_types.String import String
from ..builtin_types.Integer import Float
from math import pow


funcs = [
    Function("print", py_bind=print, restype=Null),
    Function("input", py_bind=input, restype=String),
    Function("pow", py_bind=pow, restype=Float)
]
functions = {
    func.name: func for func in funcs if isinstance(func, Function)
}
