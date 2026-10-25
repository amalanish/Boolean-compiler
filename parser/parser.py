"""
parser.py
Recursive-descent parser for Boolean expressions with relational and logical operators.
Validates Boolean expressions, respects operator precedence, and builds the Abstract Syntax Tree (AST).
"""

from typing import List, Dict, Any, Optional
from errors.exceptions import ParserError
from ast_tree.ast_nodes import ASTNode, BinaryOpNode, UnaryOpNode, VariableNode, LiteralNode


class Parser:
    """Recursive-descent parser for Boolean expressions."""

    def __init__(self, tokens: List[Dict[str, Any]]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Dict[str, Any]:
        """Return the current token or a synthetic EOF token."""
        if self.pos >= len(self.tokens):
            last_tok = self.tokens[-1] if self.tokens else None
            line = last_tok["line"] if last_tok and "line" in last_tok else 1
            col = (last_tok["column"] + len(last_tok["lexeme"])) if last_tok and "column" in last_tok else 1
            return {
                "type": "EOF",
                "lexeme": "",
                "position": -1,
                "line": line,
                "column": col,
            }

        return self.tokens[self.pos]

    def accept(self, token_type: str, lexeme: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Consume a token if its type and optional lexeme match."""
        token = self.current()

        if token["type"] != token_type:
            return None

        if lexeme is not None and token["lexeme"] != lexeme:
            return None

        self.pos += 1
        return token

    def expect(self, token_type: str, lexeme: Optional[str] = None) -> Dict[str, Any]:
        """Require a token or raise a ParserError."""
        token = self.accept(token_type, lexeme)

        if token is None:
            curr = self.current()
            found = curr["lexeme"] or "end of input"
            expected = lexeme if lexeme is not None else token_type

            raise ParserError(
                message=f"Expected {expected}, found '{found}'",
                expected=expected,
                found=found,
                line=curr.get("line", 1),
                column=curr.get("column", 1)
            )

        return token

    def parse(self) -> ASTNode:
        """Parse the complete expression and ensure all tokens are consumed."""
        if not self.tokens:
            raise ParserError("Expression cannot be empty", line=1, column=1)

        node = self.parse_or()

        if self.current()["type"] != "EOF":
            token = self.current()
            raise ParserError(
                message=f"Unexpected token '{token['lexeme']}'",
                found=token['lexeme'],
                line=token.get("line", 1),
                column=token.get("column", 1)
            )

        return node

    def parse_or(self) -> ASTNode:
        """OrExpr -> AndExpr (OR AndExpr)*"""
        node = self.parse_and()

        while True:
            tok = self.accept("LOGICAL_OPERATOR", "||")
            if not tok:
                break
            right = self.parse_and()
            node = BinaryOpNode(
                left=node,
                op="||",
                right=right,
                line=tok.get("line", 1),
                column=tok.get("column", 1)
            )

        return node

    def parse_and(self) -> ASTNode:
        """AndExpr -> NotExpr (AND NotExpr)*"""
        node = self.parse_not()

        while True:
            tok = self.accept("LOGICAL_OPERATOR", "&&")
            if not tok:
                break
            right = self.parse_not()
            node = BinaryOpNode(
                left=node,
                op="&&",
                right=right,
                line=tok.get("line", 1),
                column=tok.get("column", 1)
            )

        return node

    def parse_not(self) -> ASTNode:
        """NotExpr -> NOT NotExpr | CompareExpr"""
        tok = self.accept("LOGICAL_OPERATOR", "!")
        if tok:
            operand = self.parse_not()
            return UnaryOpNode(
                op="!",
                operand=operand,
                line=tok.get("line", 1),
                column=tok.get("column", 1)
            )

        return self.parse_comparison()

    def parse_comparison(self) -> ASTNode:
        """CompareExpr -> Primary (RelOp Primary)?"""
        node = self.parse_primary()

        token = self.current()

        if (
            token["type"] == "RELATIONAL_OPERATOR"
            and token["lexeme"] in {">", "<", "==", "!=", ">=", "<="}
        ):
            operator = token["lexeme"]
            line = token.get("line", 1)
            col = token.get("column", 1)
            self.pos += 1

            right = self.parse_primary()

            node = BinaryOpNode(
                left=node,
                op=operator,
                right=right,
                line=line,
                column=col
            )

        return node

    def parse_primary(self) -> ASTNode:
        """
        Primary -> IDENTIFIER | NUMBER | BOOLEAN
                 | '(' Expression ')'
        """
        token = self.current()
        token_type = token["type"]
        value = token["lexeme"]
        line = token.get("line", 1)
        col = token.get("column", 1)

        if token_type == "IDENTIFIER":
            self.pos += 1

            if value.lower() in {"true", "false"}:
                return LiteralNode(value.lower() == "true", line=line, column=col)

            return VariableNode(value, line=line, column=col)

        if token_type == "NUMBER":
            self.pos += 1
            num_val = float(value) if "." in value else int(value)
            return LiteralNode(num_val, line=line, column=col)

        if token_type == "LPAREN":
            self.pos += 1
            node = self.parse_or()
            self.expect("RPAREN")
            return node

        found = value or "end of input"

        raise ParserError(
            message=f"Expected an identifier, number, Boolean, or '(', found '{found}'",
            expected="expression",
            found=found,
            line=line,
            column=col
        )


def parse_tokens(tokens: List[Dict[str, Any]]) -> ASTNode:
    """Public function for parsing a list of tokens into an AST."""
    return Parser(tokens).parse()
