# JoLang
#### status: not ready

So this is my programming language which I decided to name 'JoLang' (inspired by Jonathan and GoLang).

Features I implemented so far:
- shell (REPL)
- macros
- operators
- variables
- casts (only at AST level)
- function calls (only as AST level)

Currently, I am working on the parser and AST and between task to task, i add features to the shell.
I haven't implemented an interpreter yet, but the shell.

## Docs:
### macros:
`%macro any_identifier replate_with`

What does a macro do? every time that the preprocessor sees an instance of
`any_identifier`, it immediately replaces it with `replate_with`.
Note that `any_identifier` must be an identifier.
For example: `%macro 0 1` would not work, but `%macro zero 1`, would.

Example:

`%macro hello "hello"`

`hello + "world"`

the parser would not see the macro at all, but just `"hello" + "world"`.

### operators:
any operator is available, except inplace operators (`+=`, `-=`, `/=`, etc.) and binary operators (`|`, `&`, `>>`, etc.).

for example: `~v`, `!v` (negate `v`), `+v`, `-v`, `v1+v2`, `v1 % v2`.
The precedence of the operators is the same as in Python.

### variables:
variables are set via the keyword `var`, 

`var variable = any_expression`


### casts:
Currently, they are done via `[cast_to_type]expression`,
but that might be changed in the near future as
that is pretty confusing.
> `cast_to_type` can be any expression which results in a type,
> for example, `f() + g()` if somehow that expression would result
> in a type (such as `int`), then the cast would be valid.


### function calls:
You can "call" any expression, `()()`, `4()`, `(3 + 4)(3)` "hello"(), etc.

But an error would be raised if a special `__call__`-like method was not defined.