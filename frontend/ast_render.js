/**
 * ast_render.js
 * Renders the Abstract Syntax Tree (AST) into the DOM and displays compiler error messages.
 */

class ASTRenderer {
  /**
   * @param {string|HTMLElement} container - DOM element or selector where the AST will be drawn.
   */
  constructor(container) {
    this.container = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;
  }

  /**
   * Injects CSS styling required for the visual tree nodes and error boxes.
   */
  static injectStyles() {
    if (document.getElementById('ast-renderer-styles')) return;

    const style = document.createElement('style');
    style.id = 'ast-renderer-styles';
    style.textContent = `
      .ast-tree-root {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 16px;
        background: #1e1e2e;
        color: #cdd6f4;
        border-radius: 8px;
        overflow-x: auto;
      }
      .ast-node {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
        border: 1px solid transparent;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
      }
      .ast-node-binary {
        background-color: #313244;
        color: #89b4fa;
        border-color: #89b4fa;
      }
      .ast-node-unary {
        background-color: #313244;
        color: #f9e2af;
        border-color: #f9e2af;
      }
      .ast-node-variable, .ast-node-identifier {
        background-color: #313244;
        color: #a6e3a1;
        border-color: #a6e3a1;
      }
      .ast-node-literal, .ast-node-number, .ast-node-boolean {
        background-color: #313244;
        color: #f38ba8;
        border-color: #f38ba8;
      }
      .ast-node-pos {
        font-size: 10px;
        opacity: 0.6;
        margin-left: 6px;
      }
      .ast-children {
        margin-left: 24px;
        padding-left: 12px;
        border-left: 2px dashed #45475a;
        margin-top: 8px;
        margin-bottom: 8px;
      }
      .ast-branch {
        margin: 6px 0;
        position: relative;
      }
      .ast-error-card {
        background: #451b24;
        border-left: 5px solid #f38ba8;
        color: #f2cdcd;
        padding: 14px 18px;
        border-radius: 6px;
        margin: 12px 0;
        font-family: monospace;
        white-space: pre-wrap;
      }
      .ast-error-card h4 {
        margin: 0 0 6px 0;
        color: #f38ba8;
        font-size: 15px;
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Main render function for the AST JSON payload.
   * @param {Object} astJson - The AST dictionary produced by ast_nodes.to_dict()
   */
  renderTree(astJson) {
    if (!this.container) return;
    ASTRenderer.injectStyles();
    this.container.innerHTML = '';

    if (!astJson) {
      this.container.innerHTML = '<p style="color: #6c7086;">No AST to display.</p>';
      return;
    }

    const rootWrapper = document.createElement('div');
    rootWrapper.className = 'ast-tree-root';
    rootWrapper.appendChild(this._createNodeElement(astJson));
    this.container.appendChild(rootWrapper);
  }

  /**
   * Recursively builds DOM branches and badges for each node.
   * @private
   */
  _createNodeElement(node) {
    const branch = document.createElement('div');
    branch.className = 'ast-branch';

    const nodeBadge = document.createElement('span');
    const nodeType = (node.type || 'unknown').toLowerCase();
    nodeBadge.className = `ast-node ast-node-${nodeType}`;

    let label = node.name || node.operator || node.type;
    nodeBadge.innerHTML = `<span>${label}</span>`;

    if (node.line && node.column) {
      const pos = document.createElement('span');
      pos.className = 'ast-node-pos';
      pos.textContent = `[${node.line}:${node.column}]`;
      nodeBadge.appendChild(pos);
    }

    branch.appendChild(nodeBadge);

    // Recursively append children if any exist
    if (node.children && node.children.length > 0) {
      const childrenWrapper = document.createElement('div');
      childrenWrapper.className = 'ast-children';

      node.children.forEach(child => {
        childrenWrapper.appendChild(this._createNodeElement(child));
      });

      branch.appendChild(childrenWrapper);
    }

    return branch;
  }

  /**
   * Formats and renders compile-time / syntax / semantic errors in the container.
   * @param {Object|string} error - The error object or string message from backend
   */
  renderError(error) {
    if (!this.container) return;
    ASTRenderer.injectStyles();
    this.container.innerHTML = '';

    const errorBox = document.createElement('div');
    errorBox.className = 'ast-error-card';

    if (typeof error === 'string') {
      errorBox.textContent = error;
    } else {
      const title = error.error_type || 'Compilation Error';
      const details = error.formatted || error.message || JSON.stringify(error, null, 2);
      errorBox.innerHTML = `<h4>⚠️ ${title}</h4><div>${details}</div>`;
    }

    this.container.appendChild(errorBox);
  }
}

// Global export / module export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ASTRenderer;
} else {
  window.ASTRenderer = ASTRenderer;
}
