from ..builtin_types.Function import Function
from ..builtin_types.Null import Null
from ..builtin_types.String import String


funcs = [
    Function("print", py_bind=print, restype=Null),
    Function("input", py_bind=input, restype=String)
]
functions = {
    func.name: func for func in funcs if isinstance(func, Function)
}
