import typing
from pprint import pformat
from collections import defaultdict


TEMPLATE: str = """# This file was automatically generated, any changes to it will be overridden!


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
            content = f":{{self.content!r}}"
        return f"{{self.name}}{{content}}"

    __str__ = __repr__


{}{}

def one_char(char: str) -> typing.Optional[Token]:
    return groups[1].get(char)
    
    
def two_chars(chars: str) -> typing.Optional[Token]:
    return groups[2].get(chars)
    
    
def three_chars(chars: str) -> typing.Optional[Token]:
    return groups[3].get(chars)
"""


class Repr(str):
    def __repr__(self):
        return str(self)


def uppercase_to_pascal_case(string: str) -> str:
    return "".join(chunk.title() for chunk in string.split("_"))


def generate_tokens(
        gen_to_file: str = "tokens.py",
        read_from_file: str = "tokens"
):
    tokens = ""
    groups: typing.DefaultDict[int, typing.Dict[str, str]] = defaultdict(dict)

    with open(gen_to_file, "w") as gen_file:
        with open(read_from_file, "r") as tokens_file:
            for token in tokens_file:
                token = token.strip()
                if not token or token.startswith('#'):
                    continue
                n_group, token_type, comment = token.split(" ")
                if comment and not int(n_group):
                    tokens += f"{uppercase_to_pascal_case(token_type)} = Token({token_type!r})  # {comment}\n"
                elif comment and int(n_group):
                    tokens += f"{uppercase_to_pascal_case(token_type)} = Token({token_type!r}, {comment!r})\n"
                    groups[int(n_group)][comment] = Repr(uppercase_to_pascal_case(token_type))
        formatted_groups = f"\n\ngroups = {pformat(dict(groups), indent=0)}\n"
        gen_file.write(TEMPLATE.format(tokens, formatted_groups))


generate_tokens()
