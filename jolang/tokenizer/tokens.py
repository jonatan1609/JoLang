# This file was automatically generated, any changes to it will be overridden!


import typing


class Token:
    def __init__(self, name: str, value: str = None):
        self.name = name
        self.value = value
        self.content = None

    def set_content(self, content: typing.Any) -> "Token":
        new_self = type(self)(self.name)
        new_self.content = content
        return new_self
        
    def __repr__(self) -> str:
        content = ""
        if self.content:
            content = f":{self.content!r}"
        return f"{self.name}{content}"
    
    def __instancecheck__(self, instance: "Token") -> bool:
        return self.name == instance.name
   
    __str__ = __repr__


Identifier = Token('IDENTIFIER')  # abc_def
String = Token('STRING')  # "abc_def"
Integer = Token('INTEGER')  # 123
Float = Token('FLOAT')  # 123.456
Add = Token('ADD', '+')
Subtract = Token('SUBTRACT', '-')
Equals = Token('EQUALS', '=')
Colon = Token('COLON', ':')
UnaryTilde = Token('UNARY_TILDE', '~')
Dot = Token('DOT', '.')
Comma = Token('COMMA', ',')
Backslash = Token('BACKSLASH', '\\')
Multiply = Token('MULTIPLY', '*')
Divide = Token('DIVIDE', '/')
Comment = Token('COMMENT', '$')
Modulo = Token('MODULO', '%')
Xor = Token('XOR', '^')
BinAnd = Token('BIN_AND', '&')
BinOr = Token('BIN_OR', '|')
LeftParen = Token('LEFT_PAREN', '(')
RightParen = Token('RIGHT_PAREN', ')')
LeftBracket = Token('LEFT_BRACKET', '[')
RightBracket = Token('RIGHT_BRACKET', ']')
LeftBrace = Token('LEFT_BRACE', '{')
RightBrace = Token('RIGHT_BRACE', '}')
LesserThan = Token('LESSER_THAN', '<')
GreaterThan = Token('GREATER_THAN', '>')
LogicNot = Token('LOGIC_NOT', '!')
LogicAnd = Token('LOGIC_AND', '&&')
LogicOr = Token('LOGIC_OR', '||')
NotEqual = Token('NOT_EQUAL', '!=')
IsEqual = Token('IS_EQUAL', '==')
LessEqual = Token('LESS_EQUAL', '<=')
GreatEqual = Token('GREAT_EQUAL', '>=')
InplaceAdd = Token('INPLACE_ADD', '+=')
InplaceSubtract = Token('INPLACE_SUBTRACT', '-=')
InplaceMultiply = Token('INPLACE_MULTIPLY', '*=')
InplaceDivide = Token('INPLACE_DIVIDE', '/=')
InplaceModulo = Token('INPLACE_MODULO', '%=')
InplaceXor = Token('INPLACE_XOR', '^=')
InplaceBinAnd = Token('INPLACE_BIN_AND', '&=')
InplaceBinOr = Token('INPLACE_BIN_OR', '|=')
LeftShift = Token('LEFT_SHIFT', '<<')
RightShift = Token('RIGHT_SHIFT', '>>')
InplaceLeftShift = Token('INPLACE_LEFT_SHIFT', '<<=')
InplaceRightShift = Token('INPLACE_RIGHT_SHIFT', '>>=')


groups = {1: {'!': LogicNot,
   '$': Comment,
   '%': Modulo,
   '&': BinAnd,
   '(': LeftParen,
   ')': RightParen,
   '*': Multiply,
   '+': Add,
   ',': Comma,
   '-': Subtract,
   '.': Dot,
   '/': Divide,
   ':': Colon,
   '<': LesserThan,
   '=': Equals,
   '>': GreaterThan,
   '[': LeftBracket,
   '\\': Backslash,
   ']': RightBracket,
   '^': Xor,
   '{': LeftBrace,
   '|': BinOr,
   '}': RightBrace,
   '~': UnaryTilde},
2: {'!=': NotEqual,
   '%=': InplaceModulo,
   '&&': LogicAnd,
   '&=': InplaceBinAnd,
   '*=': InplaceMultiply,
   '+=': InplaceAdd,
   '-=': InplaceSubtract,
   '/=': InplaceDivide,
   '<<': LeftShift,
   '<=': LessEqual,
   '==': IsEqual,
   '>=': GreatEqual,
   '>>': RightShift,
   '^=': InplaceXor,
   '|=': InplaceBinOr,
   '||': LogicOr},
3: {'<<=': InplaceLeftShift, '>>=': InplaceRightShift}}


def one_char(char: str) -> typing.Optional[Token]:
    return groups[1].get(char)
    
    
def two_chars(chars: str) -> typing.Optional[Token]:
    return groups[2].get(chars)
    
    
def three_chars(chars: str) -> typing.Optional[Token]:
    return groups[3].get(chars)
