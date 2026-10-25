import re
from errors.exceptions import LexerError, LexicalError

TOKEN_SPECIFICATION = [
    ("NUMBER", r"\d+(?:\.\d+)?"),
    ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("RELATIONAL_OPERATOR", r"==|!=|>=|<=|>|<"),
    ("LOGICAL_OPERATOR", r"&&|\|\||!"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("WHITESPACE", r"\s+"),
]

MASTER_PATTERN = re.compile(
    "|".join(
        f"(?P<{name}>{pattern})"
        for name, pattern in TOKEN_SPECIFICATION
    )
)


def tokenize(expression):
    tokens = []
    position = 0
    length = len(expression)

    while position < length:
        match = MASTER_PATTERN.match(expression, position)

        # Calculate current 1-indexed line and column
        line = expression[:position].count("\n") + 1
        last_newline = expression[:position].rfind("\n")
        column = (position - last_newline) if last_newline != -1 else (position + 1)

        if not match:
            character = expression[position]
            raise LexicalError(
                char=character,
                line=line,
                column=column,
                source_code=expression
            )

        token_type = match.lastgroup
        lexeme = match.group()

        if token_type != "WHITESPACE":
            tokens.append({
                "lexeme": lexeme,
                "type": token_type,
                "position": position,
                "line": line,
                "column": column,
            })

        position = match.end()

    return tokens


if __name__ == "__main__":
    expression = input("Enter a Boolean expression: ")

    try:
        result = tokenize(expression)

        print("\nTOKEN ANALYSIS")
        print("-" * 50)

        for token in result:
            print(
                f"Lexeme: {token['lexeme']:<10} "
                f"Type: {token['type']:<22} "
                f"Pos: {token['position']:<4} "
                f"[{token['line']}:{token['column']}]"
            )

        print("\nLexical analysis completed successfully.")

    except LexerError as error:
        print("\nLEXICAL ERROR:\n", error)
