"""
semantic_analyzer.py
Performs semantic analysis and validation on the Boolean Expression AST:
1. Collects all unique identifiers/variables.
2. Validates supported operators and operand counts (arity).
3. Verifies variable binding / assignment coverage for evaluation.
4. Detects constant / tautological expressions (optional optimization).
"""

from typing import Set, Dict, List, Optional, Any
from ast_tree.ast_nodes import ASTNode, BinaryOpNode, UnaryOpNode, VariableNode, LiteralNode
from errors.exceptions import SemanticError


class SemanticAnalyzer:
    """Performs semantic analysis on a parsed boolean AST."""

    # Supported operations in the boolean compiler including relational and logical
    VALID_BINARY_OPS = {
        ">", "<", "==", "!=", ">=", "<=",
        "&&", "||",
        "AND", "OR", "XOR", "NAND", "NOR", "XNOR", "IMPLIES", "IFF",
        "^", "->", "<->"
    }
    VALID_UNARY_OPS = {"!", "NOT", "~"}

    def __init__(self):
        self.variables: Set[str] = set()
        self.errors: List[str] = []

    def analyze(self, root: Any) -> Dict[str, Any]:
        """
        Runs complete semantic validation on the AST root.
        Returns a dictionary containing extracted metadata and analysis results.
        """
        self.variables.clear()
        self.errors.clear()

        if root is None:
            raise SemanticError("AST root is None, cannot perform semantic analysis.")

        # Step 1: Traverse and collect identifiers + validate operators
        self._traverse(root)

        if self.errors:
            raise SemanticError("; ".join(self.errors))

        return {
            "valid": True,
            "variables": sorted(list(self.variables)),
            "variable_count": len(self.variables),
            "is_constant": len(self.variables) == 0
        }

    def _traverse(self, node: Any) -> None:
        """Recursively checks node types, supported operators, and symbols."""
        if isinstance(node, BinaryOpNode):
            op = node.op
            if op not in self.VALID_BINARY_OPS:
                self.errors.append(
                    f"Unsupported binary operator '{op}' at line {node.line}, column {node.column}"
                )
            if node.left is None or node.right is None:
                self.errors.append(
                    f"Binary operator '{op}' requires two operands at line {node.line}, column {node.column}"
                )
            if node.left:
                self._traverse(node.left)
            if node.right:
                self._traverse(node.right)

        elif isinstance(node, UnaryOpNode):
            op = node.op
            if op not in self.VALID_UNARY_OPS:
                self.errors.append(
                    f"Unsupported unary operator '{op}' at line {node.line}, column {node.column}"
                )
            if node.operand is None:
                self.errors.append(
                    f"Unary operator '{op}' requires an operand at line {node.line}, column {node.column}"
                )
            else:
                self._traverse(node.operand)

        elif isinstance(node, VariableNode):
            if not node.name or not node.name.strip():
                self.errors.append(
                    f"Empty variable identifier found at line {node.line}, column {node.column}"
                )
            else:
                self.variables.add(node.name)

        elif isinstance(node, LiteralNode):
            # Literals are valid numbers or booleans
            pass

        elif isinstance(node, dict):
            # Dict fallback for legacy / serialized structures
            node_type = node.get("type", "")
            if node_type == "binary":
                op = node.get("operator", "")
                if op not in self.VALID_BINARY_OPS:
                    self.errors.append(f"Unsupported binary operator '{op}'")
                if "left" in node:
                    self._traverse(node["left"])
                if "right" in node:
                    self._traverse(node["right"])
            elif node_type == "unary":
                op = node.get("operator", "")
                if op not in self.VALID_UNARY_OPS:
                    self.errors.append(f"Unsupported unary operator '{op}'")
                if "operand" in node:
                    self._traverse(node["operand"])
            elif node_type == "identifier":
                val = node.get("value") or node.get("name")
                if val:
                    self.variables.add(val)
            elif node_type in ("literal", "number", "boolean"):
                pass
            else:
                self.errors.append(f"Unknown AST node dictionary: {node_type}")

        else:
            self.errors.append(f"Unknown AST node encountered: {type(node).__name__}")

    def check_variable_bindings(self, root: Any, env: Dict[str, bool]) -> None:
        """
        Ensures all variables in the expression have a corresponding value in the evaluation environment.
        """
        self.analyze(root)
        missing_vars = [var for var in self.variables if var not in env]

        if missing_vars:
            raise SemanticError(
                f"Missing boolean value assignments for variable(s): {', '.join(missing_vars)}"
            )

    @staticmethod
    def get_symbols(root: Any) -> List[str]:
        """Convenience method to retrieve all variable names in alphabetical order."""
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(root)
        return result["variables"]
