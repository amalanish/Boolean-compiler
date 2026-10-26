"""
semantic_analyzer.py
Performs semantic analysis and validation on the Boolean Expression AST:
1. Collects all unique identifiers/variables.
2. Validates supported operators and operand counts (arity).
3. Enforces strict semantic type-checking (e.g., logical ops require booleans/relations).
4. Verifies variable binding / assignment coverage for evaluation.
5. Detects constant / tautological expressions.
"""

from typing import Set, Dict, List, Optional, Any
from ast_tree.ast_nodes import ASTNode, BinaryOpNode, UnaryOpNode, VariableNode, LiteralNode
from errors.exceptions import SemanticError

class SemanticAnalyzer:
    """Performs semantic analysis on a parsed boolean AST."""

    # Supported operations in the boolean compiler including relational and logical
    VALID_BINARY_OPS = {">", "<", "==", "!=", ">=", "<=", "&&", "||", "AND", "OR", "XOR", "NAND", "NOR", "XNOR", "IMPLIES", "IFF", "^", "->", "<->" }
    VALID_UNARY_OPS = {"!", "NOT", "~"}
    
    LOGICAL_OPS = {"&&", "||", "AND", "OR", "XOR", "NAND", "NOR", "XNOR", "IMPLIES", "IFF", "^", "->", "<->"}

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

        # Step 1: Traverse, collect identifiers, validate operators, and check types
        self._traverse(root)

        if self.errors:
            raise SemanticError("; ".join(self.errors))

        return {
            "valid": True,
            "variables": sorted(list(self.variables)),
            "variable_count": len(self.variables),
            "is_constant": len(self.variables) == 0
        }

    def _traverse(self, node: Any) -> str:
        """
        Recursively checks node types, supported operators, and symbols.
        Returns the inferred type of the node ('boolean', 'number', 'variable', or 'unknown').
        """
        if node is None:
            return "unknown"

        if isinstance(node, BinaryOpNode):
            op = node.op
            if op not in self.VALID_BINARY_OPS:
                self.errors.append(f"Unsupported binary operator '{op}' at line {node.line}, column {node.column}")

            if node.left is None or node.right is None:
                self.errors.append(f"Binary operator '{op}' requires two operands at line {node.line}, column {node.column}")
                return "unknown"

            left_type = self._traverse(node.left)
            right_type = self._traverse(node.right)

            line = getattr(node, 'line', 1)
            col = getattr(node, 'column', 1)

            # Enforce semantic rule: Logical operators cannot directly take raw numbers
            if op in self.LOGICAL_OPS:
                if left_type == "number" or right_type == "number":
                    self.errors.append(f"Semantic Error: Logical operator '{op}' cannot be applied to number types at line {line}, column {col}")

            # Enforce semantic rule: Relational operators type mismatch checking (e.g., comparing boolean to number/literal)
            if op in {">", "<", "==", "!=", ">=", "<="}:
                if {left_type, right_type} == {"boolean", "number"}:
                    self.errors.append(f"Semantic Error: Type mismatch. Cannot apply relational operator '{op}' between boolean and number types at line {line}, column {col}")
                return "boolean"
            
            return "boolean" if op in self.LOGICAL_OPS else "unknown"

        elif isinstance(node, UnaryOpNode):
            op = node.op
            if op not in self.VALID_UNARY_OPS:
                self.errors.append(f"Unsupported unary operator '{op}' at line {node.line}, column {node.column}")

            if node.operand is None:
                self.errors.append(f"Unary operator '{op}' requires an operand at line {node.line}, column {node.column}")
                return "unknown"
            
            operand_type = self._traverse(node.operand)
            if op in {"!", "NOT", "~"} and operand_type == "number":
                line = getattr(node, 'line', 1)
                col = getattr(node, 'column', 1)
                self.errors.append(f"Semantic Error: Unary operator '{op}' cannot be applied to a number type at line {line}, column {col}")

            return "boolean"

        elif isinstance(node, VariableNode):
            if not node.name or not node.name.strip():
                self.errors.append(f"Empty variable identifier found at line {node.line}, column {node.column}")
            else:
                self.variables.add(node.name)
            return "variable"

        elif isinstance(node, LiteralNode):
            val = getattr(node, 'value', None)
            if isinstance(val, bool) or str(val).lower() in ("true", "false"):
                return "boolean"
            elif isinstance(val, (int, float)) or (isinstance(val, str) and val.isdigit()):
                return "number"
            return "boolean"

        elif isinstance(node, dict):
            node_type = node.get("type", "")
            if node_type == "binary":
                op = node.get("operator", "")
                if op not in self.VALID_BINARY_OPS:
                    self.errors.append(f"Unsupported binary operator '{op}'")
                if "left" in node:
                    self._traverse(node["left"])
                if "right" in node:
                    self._traverse(node["right"])
                return "boolean"
            elif node_type == "unary":
                op = node.get("operator", "")
                if op not in self.VALID_UNARY_OPS:
                    self.errors.append(f"Unsupported unary operator '{op}'")
                if "operand" in node:
                    self._traverse(node["operand"])
                return "boolean"
            elif node_type == "identifier":
                val = node.get("value") or node.get("name")
                if val:
                    self.variables.add(val)
                return "variable"
            elif node_type in ("literal", "number"):
                return "number"
            elif node_type == "boolean":
                return "boolean"
            else:
                self.errors.append(f"Unknown AST node dictionary: {node_type}")
                return "unknown"
        else:
            self.errors.append(f"Unknown AST node encountered: {type(node).__name__}")
            return "unknown"

    def check_variable_bindings(self, root: Any, env: Dict[str, bool]) -> None:
        """
        Ensures all variables in the expression have a corresponding value in the evaluation environment.
        """
        self.analyze(root)
        missing_vars = [var for var in self.variables if var not in env]
        if missing_vars:
            raise SemanticError(f"Missing boolean value assignments for variable(s): {', '.join(missing_vars)}")

    @staticmethod
    def get_symbols(root: Any) -> List[str]:
        """Convenience method to retrieve all variable names in alphabetical order."""
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(root)
        return result["variables"]
