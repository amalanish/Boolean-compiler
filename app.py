import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Ensure current directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from errors.exceptions import CompilerError, LexerError, ParserError, SemanticError
from lexer.lexer import tokenize, LexicalError
from parser.parser import parse_tokens
from ast_tree.ast_visualizer import ASTVisualizer
from semantics.semantic_analyzer import SemanticAnalyzer

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

@app.route("/")
def index():
    """Serve the frontend index.html page."""
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    """Serve frontend static assets like CSS and JS files."""
    return send_from_directory(FRONTEND_DIR, filename)

@app.route("/compile", methods=["POST"])
def compile_expression():
    """
    Compiler backend endpoint. Receives JSON: {"expression": "..."}
    Performs Lexical, Syntactic, and Semantic analysis.
    Returns tokens, syntax validation status, AST, ASCII tree, and semantic metadata.
    """
    data = request.get_json(silent=True) or {}
    expression = data.get("expression")

    if expression is None:
        return jsonify({
            "valid": False, 
            "error": "No 'expression' field provided in request body.", 
            "tokens": [], 
            "ast": None
        }), 200

    expression = expression.strip()
    if not expression:
        return jsonify({
            "valid": False, 
            "error": "Expression cannot be empty.", 
            "tokens": [], 
            "ast": None
        }), 200

    tokens = []

    # 1. Lexical Analysis
    try:
        tokens = tokenize(expression)
    except (LexerError, LexicalError) as err:
        err_msg = err.format_error() if hasattr(err, "format_error") else str(err)
        return jsonify({
            "valid": False, 
            "error": f"Lexical Error:\n{err_msg}", 
            "tokens": tokens, 
            "ast": None
        }), 200
    except Exception as err:
        return jsonify({
            "valid": False, 
            "error": f"Lexer Error: {str(err)}", 
            "tokens": tokens, 
            "ast": None
        }), 200

    # 2. Syntax Analysis & AST Generation
    try:
        ast_root = parse_tokens(tokens)
    except (ParserError, SyntaxError) as err:
        err_msg = err.format_error() if hasattr(err, "format_error") else str(err)
        return jsonify({
            "valid": False, 
            "error": f"Syntax Error:\n{err_msg}", 
            "tokens": tokens, 
            "ast": None
        }), 200
    except Exception as err:
        return jsonify({
            "valid": False, 
            "error": f"Parser Error: {str(err)}", 
            "tokens": tokens, 
            "ast": None
        }), 200

    # 3. Semantic Analysis
    try:
        analyzer = SemanticAnalyzer()
        semantic_info = analyzer.analyze(ast_root)
        
        # Explicit check if semantic result flags internal errors or validity issues
        if isinstance(semantic_info, dict) and not semantic_info.get("valid", True):
            err_msg = semantic_info.get("error", "Unknown Semantic Error")
            return jsonify({
                "valid": False,
                "error": f"Semantic Error:\n{err_msg}",
                "tokens": tokens,
                "ast": ast_root.to_dict() if hasattr(ast_root, "to_dict") else None
            }), 200

    except SemanticError as err:
        err_msg = err.format_error() if hasattr(err, "format_error") else str(err)
        return jsonify({
            "valid": False, 
            "error": f"Semantic Error:\n{err_msg}", 
            "tokens": tokens, 
            "ast": ast_root.to_dict() if hasattr(ast_root, "to_dict") else None
        }), 200
    except Exception as err:
        return jsonify({
            "valid": False, 
            "error": f"Semantic Error: {str(err)}", 
            "tokens": tokens, 
            "ast": ast_root.to_dict() if hasattr(ast_root, "to_dict") else None
        }), 200

    # 4. AST Visualizations
    ast_dict = ast_root.to_dict() if hasattr(ast_root, "to_dict") else ast_root
    ascii_tree = ASTVisualizer.to_ascii_tree(ast_root)

    return jsonify({
        "valid": True,
        "tokens": tokens,
        "ast": ast_dict,
        "ascii_tree": ascii_tree,
        "semantics": semantic_info,
        "message": "Expression compiled, parsed, and semantically verified successfully."
    }), 200

@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Boolean Expression Compiler Backend",
        "version": "2.0.0"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"==================================================")
    print(f" Boolean Expression Compiler Backend is running! ")
    print(f" Web UI: http://127.0.0.1:{port}                 ")
    print(f" API:    http://127.0.0.1:{port}/compile         ")
    print(f"==================================================")
    app.run(host="0.0.0.0", port=port, debug=True)
