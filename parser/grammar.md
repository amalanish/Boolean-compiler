
# Boolean Expression Compiler — Grammar

## Context-Free Grammar

Expression  -> OrExpr
OrExpr      -> AndExpr ( OR AndExpr )*
AndExpr     -> NotExpr ( AND NotExpr )*
NotExpr     -> NOT NotExpr | CompareExpr
CompareExpr -> Primary ( RelOp Primary )?
RelOp       -> GT | LT | EQ | NE
Primary     -> IDENTIFIER | NUMBER | BOOLEAN
             | LPAREN Expression RPAREN

## Operator Precedence

1. Parentheses
2. Relational operators: >, <, ==, !=
3. Logical NOT: !
4. Logical AND: &&
5. Logical OR: ||

## Grammar Transformation

A left-recursive rule such as:

E -> E OR T | T

can be transformed into:

E  -> T E'
E' -> OR T E' | epsilon

The transformed grammar avoids direct left recursion and is
suitable for recursive-descent parsing.

## Parsing Technique

The parser uses recursive-descent parsing. Each function
implements one grammar level and calls the next level.

## Syntax Validation

The parser rejects missing operands, unmatched parentheses,
unexpected tokens, and incomplete expressions.
