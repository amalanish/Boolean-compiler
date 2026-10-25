// Boolean Expression Compiler - Frontend JavaScript

// Connect to backend (relative /compile when served, or localhost:5000 when opened via file://)
const API_URL = window.location.protocol === "file:" ? "http://127.0.0.1:5000/compile" : "/compile";

const form = document.getElementById("compile-form");
const expressionInput = document.getElementById("expression");
const clearButton = document.getElementById("clear-btn");

const message = document.getElementById("message");
const tokensOutput = document.getElementById("tokens-output");
const syntaxOutput = document.getElementById("syntax-output");
const astOutput = document.getElementById("ast-output");
const visualTreeContainer = document.getElementById("ast-visual-tree");

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    }[character]));
}

function showMessage(text, type = "") {
    message.className = `message ${type}`.trim();
    message.textContent = text;
}

function resetResults() {
    tokensOutput.innerHTML =
        '<p class="placeholder">No tokens yet</p>';

    syntaxOutput.innerHTML =
        '<p class="placeholder">Waiting for analysis</p>';

    if (visualTreeContainer) {
        visualTreeContainer.innerHTML = "";
    }

    astOutput.textContent = "No tree generated";
    astOutput.className = "placeholder";
}

function displayTokens(tokens) {
    if (!Array.isArray(tokens) || tokens.length === 0) {
        tokensOutput.innerHTML =
            '<p class="placeholder">No token data returned</p>';
        return;
    }

    let html = `
        <table class="result-table">
            <thead>
                <tr>
                    <th>LEXEME</th>
                    <th>TOKEN TYPE</th>
                    <th>POS</th>
                </tr>
            </thead>
            <tbody>
    `;

    tokens.forEach(token => {
        const lexeme = token.lexeme ?? token.value ?? "";
        const type = token.type ?? token.token_type ?? "TOKEN";
        const pos = (token.line && token.column) 
            ? `${token.line}:${token.column}` 
            : (token.position ?? "-");

        html += `
            <tr>
                <td><code>${escapeHtml(lexeme)}</code></td>
                <td><span class="token-badge">${escapeHtml(type)}</span></td>
                <td><small>${escapeHtml(pos)}</small></td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    tokensOutput.innerHTML = html;
}

function displaySyntax(data) {
    const valid = Boolean(
        data.valid ?? data.is_valid ?? data.success
    );

    const error = data.error ?? data.message ?? "";
    const sem = data.semantics;

    if (valid) {
        let semHtml = "";
        if (sem && sem.variables) {
            const varList = sem.variables.length > 0
                ? sem.variables.map(v => `<code>${escapeHtml(v)}</code>`).join(", ")
                : "<em>None (constant expression)</em>";

            semHtml = `
                <div style="margin-top: 10px; font-size: 0.88rem; line-height: 1.4;">
                    <div><strong>Variables Detected:</strong> ${varList}</div>
                    <div><strong>Variable Count:</strong> ${sem.variable_count ?? sem.variables.length}</div>
                    <div><strong>Is Constant:</strong> ${sem.is_constant ? "Yes" : "No"}</div>
                </div>
            `;
        }

        syntaxOutput.innerHTML = `
            <div class="syntax-valid">
                <strong>✓ Valid Expression</strong>
                <p>Syntactically and semantically correct.</p>
                ${semHtml}
            </div>
        `;
    } else {
        syntaxOutput.innerHTML = `
            <div class="syntax-invalid">
                <strong>✕ Compilation Error</strong>
                <pre style="white-space: pre-wrap; font-family: monospace; margin-top: 6px;">${escapeHtml(error)}</pre>
            </div>
        `;
    }
}

function displayAST(data) {
    const ast = data.ast ?? data.parse_tree;
    const asciiTree = data.ascii_tree;

    // 1. Render interactive visual node tree via ASTRenderer
    if (visualTreeContainer && window.ASTRenderer) {
        const renderer = new window.ASTRenderer(visualTreeContainer);
        if (ast) {
            renderer.renderTree(ast);
        } else if (data.error) {
            renderer.renderError(data.error);
        }
    }

    // 2. Render ASCII tree or formatted JSON in pre block
    if (asciiTree) {
        astOutput.className = "";
        astOutput.textContent = asciiTree;
    } else if (ast !== undefined && ast !== null && ast !== "") {
        astOutput.className = "";
        astOutput.textContent = typeof ast === "string" ? ast : JSON.stringify(ast, null, 2);
    } else {
        astOutput.textContent = "No tree generated";
        astOutput.className = "placeholder";
    }
}

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const expression = expressionInput.value.trim();

    if (!expression) {
        showMessage(
            "Please enter a Boolean expression before compiling.",
            "error"
        );
        expressionInput.focus();
        return;
    }

    resetResults();

    showMessage(
        "Compiling expression through lexer, parser, and semantic analyzer..."
    );

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                expression: expression
            })
        });

        if (!response.ok) {
            throw new Error(
                `Server returned status ${response.status}.`
            );
        }

        const data = await response.json();

        displayTokens(data.tokens ?? data.token_list);
        displaySyntax(data);
        displayAST(data);

        if (data.valid) {
            showMessage(
                "Analysis completed successfully. Tokens, AST, and semantics generated.",
                "success"
            );
        } else {
            showMessage(
                "Compilation completed with errors. See details below.",
                "error"
            );
        }

    } catch (error) {
        showMessage(
            "Could not connect to the compiler backend. " +
            "Make sure the Flask server is running at http://127.0.0.1:5000. Details: " + error.message,
            "error"
        );
    }
});

// Fill the input box when an example is clicked.
document.querySelectorAll(".example-btn").forEach(button => {
    button.addEventListener("click", function () {
        expressionInput.value = this.dataset.expression;
        expressionInput.focus();
    });
});

// Clear the input and results.
clearButton.addEventListener("click", function () {
    expressionInput.value = "";
    resetResults();

    showMessage(
        "Enter an expression and connect the compiler backend to view results."
    );

    expressionInput.focus();
});
