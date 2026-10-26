// Boolean Expression Compiler - Frontend JavaScript

// Connect to backend (relative /compile when served, or localhost:5000 when opened via file://)
const API_URL = window.location.protocol === "file:" ? "http://127.0.0.1:5000/compile" : "/compile";

const form = document.getElementById("compile-form");
const expressionInput = document.getElementById("expression");
const clearButton = document.getElementById("clear-btn");

const message = document.getElementById("message");
const tokensOutput = document.getElementById("tokens-output");
const syntaxOutput = document.getElementById("syntax-output");
const semanticOutput = document.getElementById("semantic-output");
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

    semanticOutput.innerHTML =
        '<p class="placeholder">Waiting for semantic analysis</p>';

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

/**
 * Displays the Syntax (parser) result card.
 * Shows valid if parsing succeeded; shows the specific error if it's a
 * lexical or syntax error. Does NOT show semantic errors here.
 */
function displaySyntax(data) {
    const errorType = data.error_type ?? "";
    const error = data.error ?? data.message ?? "";

    // If failed at lexical or syntax stage, show the error here
    if (!data.valid && (errorType === "lexical" || errorType === "syntax" || errorType === "")) {
        // For backward compat: fall back to showing any non-semantic error
        if (errorType !== "semantic") {
            syntaxOutput.innerHTML = `
                <div class="syntax-invalid">
                    <strong>&#10007; ${errorType === "lexical" ? "Lexical" : "Syntax"} Error</strong>
                    <pre style="white-space: pre-wrap; font-family: monospace; margin-top: 6px;">${escapeHtml(error)}</pre>
                </div>
            `;
            return;
        }
    }

    // If we reach here parsing was OK (might still have semantic error)
    syntaxOutput.innerHTML = `
        <div class="syntax-valid">
            <strong>&#10003; Syntax Valid</strong>
            <p>Expression parsed successfully &mdash; no grammar errors.</p>
        </div>
    `;
}

/**
 * Displays the Semantic Analysis result card.
 * Shows variable metadata on success, or a clear semantic error panel on failure.
 * If the error happened before semantic analysis (lexical/syntax stage),
 * shows a "skipped" notice.
 */
function displaySemantics(data) {
    const errorType = data.error_type ?? "";
    const error = data.error ?? "";
    const sem = data.semantics;

    // Expression failed before reaching semantic analysis
    if (!data.valid && errorType !== "semantic") {
        semanticOutput.innerHTML = `
            <div class="semantic-skipped">
                <strong>&#8212; Skipped</strong>
                <p style="margin-top:6px;">Semantic analysis is skipped because ${errorType === "lexical" ? "lexical" : "syntax"} errors were found first. Fix those errors and recompile.</p>
            </div>
        `;
        return;
    }

    // Semantic error found
    if (!data.valid && errorType === "semantic") {
        // Strip the "Semantic Error:\n" prefix for a cleaner display
        const rawMsg = error.replace(/^Semantic Error:\n?/i, "").trim();
        semanticOutput.innerHTML = `
            <div class="semantic-error">
                <strong>&#9888; Semantic Error</strong>
                <pre style="white-space: pre-wrap; font-family: monospace; margin-top: 8px; font-size: 12px;">${escapeHtml(rawMsg)}</pre>
            </div>
        `;
        return;
    }

    // Semantic analysis passed
    if (sem) {
        const isConstant = sem.is_constant ?? (sem.variables && sem.variables.length === 0);
        const varCount = sem.variable_count ?? (sem.variables ? sem.variables.length : 0);

        let varBadges = "";
        if (sem.variables && sem.variables.length > 0) {
            varBadges = sem.variables
                .map(v => `<span class="sem-badge">${escapeHtml(v)}</span>`)
                .join(" ");
        } else {
            varBadges = "<em>None &mdash; constant expression</em>";
        }

        semanticOutput.innerHTML = `
            <div class="semantic-valid">
                <strong>&#10003; Semantically Valid</strong>
                <div style="margin-top: 10px; font-size: 0.88rem; line-height: 1.8;">
                    <div><strong>Variables Detected:</strong><br>${varBadges}</div>
                    <div style="margin-top:6px;"><strong>Variable Count:</strong> ${varCount}</div>
                    <div><strong>Is Constant:</strong> ${isConstant ? "Yes" : "No"}</div>
                </div>
            </div>
        `;
    } else {
        semanticOutput.innerHTML = `
            <div class="semantic-valid">
                <strong>&#10003; Semantically Valid</strong>
                <p style="margin-top:6px;">No semantic issues detected.</p>
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
        displaySemantics(data);
        displayAST(data);

        if (data.valid) {
            showMessage(
                "Analysis completed successfully. Tokens, AST, and semantics generated.",
                "success"
            );
        } else {
            const errorType = data.error_type ?? "unknown";
            const label = errorType === "lexical" ? "Lexical"
                : errorType === "syntax" ? "Syntax"
                : errorType === "semantic" ? "Semantic"
                : "Compilation";
            showMessage(
                `${label} error detected. See the relevant panel below for details.`,
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
