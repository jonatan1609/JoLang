# JoLang
#### status: not ready

So this is my programming language which I decided to name 'JoLang' (inspired by Jonathan and GoLang).

Features I implemented so far:
- shell (REPL)
- Comments
- macros
- operators
- variables
- functions (only at AST level )
- function calls (only at AST level)
- if statements (only at AST level)
- loops (while and for) (only at AST level)

Currently, I am working on the parser and AST and between task to task, i add features to the shell.
I haven't implemented an interpreter yet, but the shell.

## Docs:

### comments:
You can write a comment with the `$` prefix. a comment ends at the end of the line.
example:

```
$ some comment
$ another comment
```

### macros:
`%macro any_identifier replace_with`

What does a macro do? every time that the preprocessor sees an instance of
`any_identifier`, it immediately replaces it with `replace_with`.
Note that `any_identifier` must be an identifier.
For example: `%macro 0 1` would not work, but `%macro zero 1`, would.

Example:

`%macro hello "hello"`

`hello + "world"`

the parser would not see the macro at all, but just `"hello" + "world"`.

### operators:
for example: `~v`, `!v` (negate `v`), `+v`, `-v`, `v1+v2`, `v1 % v2`.
The precedence of the operators is the same as in Python (Except `!`,`+`, `-`, `~` which have the highest precedence after `()`).

### variables:
variables are set like that: 

`variable = any_expression`

note that assignment is considered an expression and not an assignment, 
so it's possible to do stuff like `(a = 2)` and also `(a = b = c = 2)` and even
inplace operators `(a += b -= c = 2)` which will assign `2` to `c`
and then subtract-assign `c` (2) from `b`, and then add-assign it back to `a`.


### functions:
you can define a function by the following syntax:

```
func thing(arg1, arg2){
 $ statements
}
```

Note that there are no keyword-arguments.

### function calls:
You can "call" any expression, `()()`, `4()`, `(3 + 4)(3)` `"hello"()`, etc.

But an error would be raised if a special `__call__`-like method was not defined.

### if statements
You can define an if statements by this syntax: `if(expression){body}`.
you can also add `elif(expr){body}` and `else{body}` blocks.

example:

```
if(a = thing()){
    do_with(a) $ a is the result of thing()
}
elif(a = another_thing()){
}
else {
}
```

### loops

There are two types of loops, a `for` loop and a `while` loop.
the `while` loop is written like `while(cond){body}` and the `for` loop
is written like `for(expr;expr;expr){body}` where `expr` can be nothing (like `(;;)`).
in case the for loop is defined as `(;;)` it would be equivalent to `while(true)`.

examples:

while:
```
while(name = getname()){
    do_with(name)
}
```
for:
```
for(i=0;i<10;i += 1){ $ there is no i++ in jolang (yet)
    do_with(i)
}
```
