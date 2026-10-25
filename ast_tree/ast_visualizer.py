"""
ast_visualizer.py
Provides utilities to visualize the Abstract Syntax Tree (AST):
1. Terminal / ASCII tree display.
2. JSON export for frontend rendering (e.g., D3.js / HTML canvas).
3. Graphviz DOT format generation for generating tree diagrams.
"""

import json
from typing import Any, Dict
from ast_tree.ast_nodes import ASTNode, BinaryOpNode, UnaryOpNode, VariableNode, LiteralNode, display_ast


class ASTVisualizer:
    """Helper class to visualize, format, and export AST nodes."""

    @staticmethod
    def to_ascii_tree(node: Any, prefix: str = "", is_last: bool = True) -> str:
        """
        Renders an ASCII tree structure suitable for console/terminal logs.
        """
        return display_ast(node, prefix, is_last)

    @staticmethod
    def to_json(node: Any, indent: int = 2) -> str:
        """
        Serializes the AST into a JSON string formatted for web frontend consumption.
        """
        if hasattr(node, "to_dict"):
            data = node.to_dict()
        else:
            data = node
        return json.dumps(data, indent=indent)

    @staticmethod
    def to_dot(node: Any) -> str:
        """
        Converts the AST to Graphviz DOT format for SVG/PNG graph generation.
        """
        lines = [
            "digraph AST {",
            '  node [fontname="Helvetica", shape=box, style="rounded,filled", fillcolor="#f0f4f8"];',
            '  edge [fontname="Helvetica"];'
        ]
        counter = [0]

        def add_nodes(curr_node: Any) -> int:
            counter[0] += 1
            node_id = counter[0]

            if isinstance(curr_node, BinaryOpNode):
                label = curr_node.op
                color = "#d1e7dd"
                lines.append(f'  node_{node_id} [label="{label}", fillcolor="{color}"];')
                left_id = add_nodes(curr_node.left)
                right_id = add_nodes(curr_node.right)
                lines.append(f"  node_{node_id} -> node_{left_id};")
                lines.append(f"  node_{node_id} -> node_{right_id};")

            elif isinstance(curr_node, UnaryOpNode):
                label = curr_node.op
                color = "#fff3cd"
                lines.append(f'  node_{node_id} [label="{label}", fillcolor="{color}"];')
                child_id = add_nodes(curr_node.operand)
                lines.append(f"  node_{node_id} -> node_{child_id};")

            elif isinstance(curr_node, VariableNode):
                label = f"Var: {curr_node.name}"
                color = "#cfe2ff"
                lines.append(f'  node_{node_id} [label="{label}", fillcolor="{color}"];')

            elif isinstance(curr_node, LiteralNode):
                label = f"Lit: {curr_node.value}"
                color = "#e2e3e5"
                lines.append(f'  node_{node_id} [label="{label}", fillcolor="{color}"];')

            elif isinstance(curr_node, dict):
                label = curr_node.get("name") or curr_node.get("operator") or curr_node.get("value") or curr_node.get("type", "node")
                lines.append(f'  node_{node_id} [label="{label}"];')
                children = curr_node.get("children", [])
                if not children:
                    if "left" in curr_node and "right" in curr_node:
                        children = [curr_node["left"], curr_node["right"]]
                    elif "operand" in curr_node:
                        children = [curr_node["operand"]]
                for child in children:
                    child_id = add_nodes(child)
                    lines.append(f"  node_{node_id} -> node_{child_id};")

            return node_id

        add_nodes(node)
        lines.append("}")
        return "\n".join(lines)


def print_ast(node: Any) -> None:
    """Convenience function to print the ASCII tree directly to console."""
    print(ASTVisualizer.to_ascii_tree(node))
