"""
exceptions.py
Standardized compiler exceptions for Lexing, Parsing, and Semantic Analysis.
Includes position markers (line, column) and visual error highlighting.
"""

from typing import Optional, Dict, Any


class CompilerError(Exception):
    """Base class for all Boolean Compiler errors."""

    def __init__(
        self,
        message: str,
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None
    ):
        self.message = message
        self.line = line
        self.column = column
        self.source_code = source_code
        super().__init__(self.format_error())

    def format_error(self) -> str:
        """Constructs a formatted, user-friendly error string with code indicator."""
        header = f"[{self.__class__.__name__}] Line {self.line}, Column {self.column}: {self.message}"
        
        # If the input expression string is provided, draw a caret pointing to the mistake
        if self.source_code:
            lines = self.source_code.splitlines()
            if 0 < self.line <= len(lines):
                target_line = lines[self.line - 1]
                pointer = " " * max(0, self.column - 1) + "^"
                return f"{header}\n    {target_line}\n    {pointer}"
        
        return header

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the error for JSON API responses in the frontend."""
        return {
            "success": False,
            "error_type": self.__class__.__name__,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "formatted": self.format_error()
        }


class LexerError(CompilerError):
    """Raised during lexical analysis when encountering invalid characters/tokens."""

    def __init__(
        self,
        char: str,
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None
    ):
        message = f"Unexpected or illegal character '{char}' at column {column}"
        super().__init__(message, line, column, source_code)



class ParserError(CompilerError, SyntaxError):
    """Raised during syntactic analysis when grammar rules fail."""

    def __init__(
        self,
        message: str,
        expected: Optional[str] = None,
        found: Optional[str] = None,
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None
    ):
        if expected and found:
            full_msg = f"{message} (Expected '{expected}', found '{found}')"
        else:
            full_msg = message
        super().__init__(full_msg, line, column, source_code)


class SemanticError(CompilerError):
    """Raised when an expression is syntactically valid but logically/semantically invalid."""

    def __init__(
        self,
        message: str,
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None
    ):
        super().__init__(message, line, column, source_code)


LexicalError = LexerError
SyntaxError_ = ParserError


