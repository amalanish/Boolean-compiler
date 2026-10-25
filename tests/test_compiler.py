import unittest
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from errors.exceptions import CompilerError, LexerError, ParserError, SemanticError, LexicalError
from lexer.lexer import tokenize
from parser.parser import Parser, parse_tokens
from ast_tree.ast_nodes import ASTNode, BinaryOpNode, UnaryOpNode, VariableNode, LiteralNode
from ast_tree.ast_visualizer import ASTVisualizer
from semantics.semantic_analyzer import SemanticAnalyzer
from app import app


class TestLexer(unittest.TestCase):
    def test_relational_operators(self):
        tokens = tokenize("a > 10 < 20 == 30 != 40 >= 50 <= 60")
        operators = [t["lexeme"] for t in tokens if t["type"] == "RELATIONAL_OPERATOR"]
        self.assertEqual(operators, [">", "<", "==", "!=", ">=", "<="])

    def test_logical_operators(self):
        tokens = tokenize("a && b || !c")
        operators = [t["lexeme"] for t in tokens if t["type"] == "LOGICAL_OPERATOR"]
        self.assertEqual(operators, ["&&", "||", "!"])

    def test_parentheses(self):
        tokens = tokenize("(a != 5)")
        parens = [(t["type"], t["lexeme"]) for t in tokens if "PAREN" in t["type"]]
        self.assertEqual(parens, [("LPAREN", "("), ("RPAREN", ")")])

    def test_token_position_tracking(self):
        tokens = tokenize("x > 5")
        self.assertEqual(tokens[0]["line"], 1)
        self.assertEqual(tokens[0]["column"], 1)
        self.assertEqual(tokens[1]["column"], 3)

    def test_invalid_character(self):
        with self.assertRaises(LexerError):
            tokenize("a @ 10")


class TestParser(unittest.TestCase):
    def test_relational_expression(self):
        tokens = tokenize("a > 10")
        ast = parse_tokens(tokens)
        self.assertEqual(ast["type"], "binary")
        self.assertEqual(ast["operator"], ">")
        self.assertEqual(ast["left"]["value"], "a")
        self.assertEqual(ast["right"]["value"], 10)

    def test_precedence_and_over_or(self):
        # In a || b && c, && has higher precedence than ||
        # Tree root should be ||, with right child &&
        tokens = tokenize("a > 1 || b < 2 && c == 3")
        ast = parse_tokens(tokens)
        self.assertEqual(ast["type"], "binary")
        self.assertEqual(ast["operator"], "||")
        self.assertEqual(ast["left"]["operator"], ">")
        self.assertEqual(ast["right"]["operator"], "&&")

    def test_parentheses_precedence(self):
        # (a || b) && c
        tokens = tokenize("(a > 1 || b < 2) && c == 3")
        ast = parse_tokens(tokens)
        self.assertEqual(ast["type"], "binary")
        self.assertEqual(ast["operator"], "&&")
        self.assertEqual(ast["left"]["operator"], "||")
        self.assertEqual(ast["right"]["operator"], "==")

    def test_not_operator(self):
        tokens = tokenize("!(a != 5)")
        ast = parse_tokens(tokens)
        self.assertEqual(ast["type"], "unary")
        self.assertEqual(ast["operator"], "!")
        self.assertEqual(ast["operand"]["operator"], "!=")

    def test_boolean_literals(self):
        tokens = tokenize("true && false")
        ast = parse_tokens(tokens)
        self.assertEqual(ast["left"]["type"], "boolean")
        self.assertEqual(ast["left"]["value"], True)
        self.assertEqual(ast["right"]["type"], "boolean")
        self.assertEqual(ast["right"]["value"], False)

    def test_syntax_errors(self):
        invalid_expressions = [
            "a >",
            "> 10",
            "(a > 10",
            "a > 10)",
            "a > 10 && && b < 20",
            "",
        ]
        for expr in invalid_expressions:
            with self.subTest(expr=expr):
                with self.assertRaises((ParserError, SyntaxError)):
                    tokens = tokenize(expr)
                    parse_tokens(tokens)


class TestSemanticsAndVisualizer(unittest.TestCase):
    def test_semantic_variable_extraction(self):
        tokens = tokenize("a > 10 && (b < 20 || !c)")
        ast = parse_tokens(tokens)
        result = SemanticAnalyzer().analyze(ast)
        self.assertTrue(result["valid"])
        self.assertEqual(result["variables"], ["a", "b", "c"])
        self.assertEqual(result["variable_count"], 3)
        self.assertFalse(result["is_constant"])

    def test_constant_expression(self):
        tokens = tokenize("10 > 5 && true")
        ast = parse_tokens(tokens)
        result = SemanticAnalyzer().analyze(ast)
        self.assertTrue(result["valid"])
        self.assertEqual(result["variables"], [])
        self.assertTrue(result["is_constant"])

    def test_ascii_tree_generation(self):
        tokens = tokenize("a > 10")
        ast = parse_tokens(tokens)
        tree_str = ASTVisualizer.to_ascii_tree(ast)
        self.assertIn(">", tree_str)
        self.assertIn("Var(a)", tree_str)
        self.assertIn("Lit(10)", tree_str)


class TestFlaskBackend(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Boolean Expression", response.data)

    def test_static_files(self):
        css_res = self.client.get("/style.css")
        self.assertEqual(css_res.status_code, 200)
        js_res = self.client.get("/script.js")
        self.assertEqual(js_res.status_code, 200)
        ast_res = self.client.get("/ast_render.js")
        self.assertEqual(ast_res.status_code, 200)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_compile_valid(self):
        response = self.client.post(
            "/compile",
            data=json.dumps({"expression": "a > 10 && b < 20"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["valid"])
        self.assertIsNotNone(data["ast"])
        self.assertIsNotNone(data["ascii_tree"])
        self.assertIn("semantics", data)
        self.assertEqual(data["semantics"]["variables"], ["a", "b"])
        self.assertIsInstance(data["tokens"], list)
        self.assertEqual(len(data["tokens"]), 7)

    def test_compile_syntax_error(self):
        response = self.client.post(
            "/compile",
            data=json.dumps({"expression": "a > 10 &&"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["valid"])
        self.assertIn("Syntax Error", data["error"])
        self.assertIsNone(data["ast"])

    def test_compile_lexical_error(self):
        response = self.client.post(
            "/compile",
            data=json.dumps({"expression": "a @ 10"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["valid"])
        self.assertIn("Lexical Error", data["error"])
        self.assertIsNone(data["ast"])

    def test_compile_empty_expression(self):
        response = self.client.post(
            "/compile",
            data=json.dumps({"expression": ""}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["valid"])
        self.assertIn("empty", data["error"].lower())


if __name__ == "__main__":
    unittest.main()
