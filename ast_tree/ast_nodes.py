"""
ast_nodes.py
Defines the Abstract Syntax Tree (AST) node structures, 
tree serialization for the frontend, and terminal display utilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ASTNode(ABC):
    """Base class for all Abstract Syntax Tree nodes."""

    def __init__(self, line: int = 1, column: int = 1):
        self.line = line
        self.column = column

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serializes the node into a dictionary for JSON/frontend visualization."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Returns a string representation of the node."""
        pass

    def __getitem__(self, item: str) -> Any:
        return self.to_dict()[item]

    def __contains__(self, item: str) -> bool:
        return item in self.to_dict()

    def get(self, item: str, default: Any = None) -> Any:
        return self.to_dict().get(item, default)


class BinaryOpNode(ASTNode):
    """Represents binary operations (e.g., &&, ||, >, <, ==, !=, >=, <=, AND, OR)."""

    def __init__(self, left: ASTNode, op: str, right: ASTNode, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.left = left
        self.op = op.upper() if op.isalpha() else op
        self.right = right

    def to_dict(self) -> Dict[str, Any]:
        left_dict = self.left.to_dict() if hasattr(self.left, "to_dict") else self.left
        right_dict = self.right.to_dict() if hasattr(self.right, "to_dict") else self.right
        return {
            "type": "binary",
            "name": self.op,
            "operator": self.op,
            "left": left_dict,
            "right": right_dict,
            "children": [left_dict, right_dict],
            "line": self.line,
            "column": self.column,
        }

    def __str__(self) -> str:
        return f"BinaryOp({self.left} {self.op} {self.right})"


class UnaryOpNode(ASTNode):
    """Represents unary boolean operations (e.g., !, NOT)."""

    def __init__(self, op: str, operand: ASTNode, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.op = op.upper() if op.isalpha() else op
        self.operand = operand

    def to_dict(self) -> Dict[str, Any]:
        operand_dict = self.operand.to_dict() if hasattr(self.operand, "to_dict") else self.operand
        return {
            "type": "unary",
            "name": self.op,
            "operator": self.op,
            "operand": operand_dict,
            "children": [operand_dict],
            "line": self.line,
            "column": self.column,
        }

    def __str__(self) -> str:
        return f"UnaryOp({self.op} {self.operand})"


class VariableNode(ASTNode):
    """Represents variable identifiers (e.g., a, b, x, y)."""

    def __init__(self, name: str, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "identifier",
            "name": self.name,
            "value": self.name,
            "children": [],
            "line": self.line,
            "column": self.column,
        }

    def __str__(self) -> str:
        return f"Var({self.name})"


class LiteralNode(ASTNode):
    """Represents boolean constants (True/False) or numeric literals (10, 3.14)."""

    def __init__(self, value: Any, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        lit_type = "boolean" if isinstance(self.value, bool) else "number"
        return {
            "type": lit_type,
            "name": str(self.value),
            "value": self.value,
            "children": [],
            "line": self.line,
            "column": self.column,
        }

    def __str__(self) -> str:
        return f"Lit({self.value})"


def display_ast(node: Any, prefix: str = "", is_last: bool = True) -> str:
    """
    Renders an ASCII tree representation of the AST for CLI / debugging.
    Supports both ASTNode instances and dictionary representations.
    """
    marker = "└── " if is_last else "├── "

    if isinstance(node, BinaryOpNode):
        display_name = node.op
        children = [node.left, node.right]
    elif isinstance(node, UnaryOpNode):
        display_name = node.op
        children = [node.operand]
    elif isinstance(node, VariableNode):
        display_name = f"Var({node.name})"
        children = []
    elif isinstance(node, LiteralNode):
        display_name = f"Lit({node.value})"
        children = []
    elif isinstance(node, dict):
        display_name = node.get("name") or node.get("operator") or node.get("type", "node")
        if node.get("type") == "identifier":
            display_name = f"Var({node.get('value', display_name)})"
        elif node.get("type") in ("boolean", "number", "literal"):
            display_name = f"Lit({node.get('value', display_name)})"
        children = node.get("children", [])
        if not children:
            if "left" in node and "right" in node:
                children = [node["left"], node["right"]]
            elif "operand" in node:
                children = [node["operand"]]
    else:
        display_name = str(node)
        children = []

    lines = [f"{prefix}{marker}{display_name}"]

    child_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(children):
        last = (i == len(children) - 1)
        lines.append(display_ast(child, child_prefix, last))

    return "\n".join(lines)
