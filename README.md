# Boolean Expression Compiler — Complete Integrated System

A full compiler front end and backend supporting relational and logical operators: `>`, `<`, `==`, `!=`, `>=`, `<=`, `&&`, `||`, and `!`. Validates Boolean expressions, respects operator precedence, runs semantic checks, and renders both interactive graphical Abstract Syntax Trees (AST) and terminal ASCII trees.

---

## 🚀 System Architecture & Modules

```
Boolean-compiler-main/
│
├── app.py                      # Flask REST API backend server & routing
├── requirements.txt            # Python dependencies (Flask, flask-cors)
├── README.md                   # Complete documentation
│
├── ast_tree/                   # Abstract Syntax Tree representation & visualization
│   ├── __init__.py
│   ├── ast_nodes.py            # AST Node hierarchy (BinaryOpNode, UnaryOpNode, VariableNode, LiteralNode)
│   └── ast_visualizer.py       # ASCII tree formatter & Graphviz DOT exporter
│
├── errors/                     # Standardized compiler exception classes
│   ├── __init__.py
│   └── exceptions.py           # CompilerError, LexerError, ParserError, SemanticError (with line/column carets)
│
├── lexer/                      # Lexical Analysis (Scanner)
│   ├── __init__.py
│   └── lexer.py                # Regex tokenization with position & coordinate tracking
│
├── parser/                     # Syntax Analysis & AST Building
│   ├── __init__.py
│   ├── grammar.md              # Formal Context-Free Grammar specification
│   └── parser.py               # Recursive-descent parser enforcing precedence
│
├── semantics/                  # Semantic Analysis
│   ├── __init__.py
│   └── semantic_analyzer.py    # Symbol collector, arity validation & constant detection
│
├── frontend/                   # Interactive Web Application
│   ├── index.html              # Modern dark-mode UI layout
│   ├── script.js               # Client controller & API connector
│   ├── ast_render.js           # Interactive visual AST renderer (DOM tree nodes)
│   └── style.css               # Clean responsive styling
│
└── tests/                      # Automated Verification
    └── test_compiler.py        # 21 unit tests covering lexer, parser, AST, semantics & API
```

---

## 📐 Grammar & Operator Precedence

The compiler strictly respects standard precedence:

1. **Parentheses**: `( ... )`
2. **Primary**: Identifiers (`a`, `b`), Numbers (`10`, `3.14`), Booleans (`true`, `false`)
3. **Relational Operators**: `>`, `<`, `==`, `!=`, `>=`, `<=`
4. **Logical NOT**: `!` (unary, right-associative)
5. **Logical AND**: `&&` (binary, left-associative)
6. **Logical OR**: `||` (binary, left-associative)

---

## 🛠️ Installation & Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Backend Server
```bash
python app.py
```
Server runs at `http://127.0.0.1:5000`.

### 3. Open in Browser
Open `http://127.0.0.1:5000` to interact with the compiler playground.

### 4. Run Automated Tests
```bash
python -m unittest discover -s tests -v
```
Runs all 21 automated tests verifying every stage of the pipeline.

---

## 📡 API Reference

### `POST /compile`
Compiles, parses, and analyzes a Boolean expression.

**Request:**
```json
{
  "expression": "a > 10 && (b < 20 || !c)"
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "tokens": [
    { "lexeme": "a", "type": "IDENTIFIER", "line": 1, "column": 1 },
    { "lexeme": ">", "type": "RELATIONAL_OPERATOR", "line": 1, "column": 3 },
    { "lexeme": "10", "type": "NUMBER", "line": 1, "column": 5 },
    { "lexeme": "&&", "type": "LOGICAL_OPERATOR", "line": 1, "column": 8 },
    { "lexeme": "(", "type": "LPAREN", "line": 1, "column": 11 },
    { "lexeme": "b", "type": "IDENTIFIER", "line": 1, "column": 12 },
    { "lexeme": "<", "type": "RELATIONAL_OPERATOR", "line": 1, "column": 14 },
    { "lexeme": "20", "type": "NUMBER", "line": 1, "column": 16 },
    { "lexeme": "||", "type": "LOGICAL_OPERATOR", "line": 1, "column": 19 },
    { "lexeme": "!", "type": "LOGICAL_OPERATOR", "line": 1, "column": 22 },
    { "lexeme": "c", "type": "IDENTIFIER", "line": 1, "column": 23 },
    { "lexeme": ")", "type": "RPAREN", "line": 1, "column": 24 }
  ],
  "ast": {
    "type": "binary",
    "operator": "&&",
    "children": [...]
  },
  "ascii_tree": "└── &&\n    ├── >\n    │   ├── Var(a)\n    │   └── Lit(10)\n    └── ||\n        ├── <\n        │   ├── Var(b)\n        │   └── Lit(20)\n        └── !\n            └── Var(c)",
  "semantics": {
    "valid": true,
    "variables": ["a", "b", "c"],
    "variable_count": 3,
    "is_constant": false
  },
  "message": "Expression compiled, parsed, and semantically verified successfully."
}
```
