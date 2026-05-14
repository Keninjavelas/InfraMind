import * as vscode from 'vscode';

export class SecurityPanel {
    public static currentPanel: SecurityPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel) {
        this._panel = panel;
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (SecurityPanel.currentPanel) {
            SecurityPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'infraMindSecurity',
            'InfraMind Security Review',
            column || vscode.ViewColumn.One,
            { enableScripts: true }
        );

        SecurityPanel.currentPanel = new SecurityPanel(panel);
    }

    public updateContent(infraSummary: any) {
        this._panel.webview.html = this._getHtmlForWebview(infraSummary);
    }

    private _getHtmlForWebview(infraSummary: any) {
        let risksHtml = '';
        if (infraSummary.security_risks && infraSummary.security_risks.length > 0) {
            risksHtml = infraSummary.security_risks.map((risk: any) => `
                <div class="risk-card">
                    <div class="risk-header">
                        <span class="severity ${risk.severity.toLowerCase()}">${risk.severity}</span>
                        <span class="category">— ${risk.category}</span>
                    </div>
                    <div class="risk-desc">${risk.description}</div>
                    <div class="risk-rec"><strong>Remediation:</strong> ${risk.recommendation}</div>
                    ${risk.resource_id ? `<div class="risk-res"><strong>Resource:</strong> <code>${risk.resource_id}</code></div>` : ''}
                </div>
            `).join('');
        } else {
            risksHtml = `<p>No security risks detected!</p>`;
        }

        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Security Review</title>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-editor-foreground);
                        background-color: var(--vscode-editor-background);
                        padding: 20px;
                    }
                    h1 {
                        font-size: 1.5em;
                        border-bottom: 1px solid var(--vscode-panel-border);
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                    }
                    .risk-card {
                        border: 1px solid var(--vscode-panel-border);
                        background-color: var(--vscode-editorWidget-background);
                        padding: 15px;
                        margin-bottom: 15px;
                        border-radius: 4px;
                    }
                    .severity {
                        font-weight: bold;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-size: 0.8em;
                    }
                    .severity.critical { background-color: var(--vscode-errorForeground); color: white; }
                    .severity.high { background-color: #d97706; color: white; }
                    .severity.medium { background-color: #ca8a04; color: white; }
                    .severity.low { background-color: #2563eb; color: white; }
                    
                    .category {
                        color: var(--vscode-descriptionForeground);
                        font-size: 0.9em;
                        margin-left: 5px;
                        text-transform: uppercase;
                    }
                    .risk-desc {
                        margin: 10px 0;
                        font-size: 1.1em;
                    }
                    .risk-rec, .risk-res {
                        font-size: 0.9em;
                        color: var(--vscode-textPreformat-foreground);
                        margin-top: 5px;
                    }
                    code {
                        background-color: var(--vscode-textCodeBlock-background);
                        padding: 2px 4px;
                        border-radius: 3px;
                    }
                </style>
            </head>
            <body>
                <h1>InfraMind Security Intelligence</h1>
                <div class="metrics">
                    <p>Total Resources: ${infraSummary.metrics?.total_resources || 0}</p>
                    <p>Complexity: <strong>${infraSummary.estimated_complexity || 'N/A'}</strong></p>
                </div>
                <h2>Security Risks</h2>
                <div class="risks-container">
                    ${risksHtml}
                </div>
            </body>
            </html>`;
    }

    public dispose() {
        SecurityPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) { x.dispose(); }
        }
    }
}
