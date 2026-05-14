import * as vscode from 'vscode';

export class ArchitecturePanel {
    public static currentPanel: ArchitecturePanel | undefined;
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

        if (ArchitecturePanel.currentPanel) {
            ArchitecturePanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'infraMindArchitecture',
            'InfraMind Architecture',
            column || vscode.ViewColumn.One,
            { enableScripts: true }
        );

        ArchitecturePanel.currentPanel = new ArchitecturePanel(panel);
    }

    public updateContent(mermaidData: string) {
        this._panel.webview.html = this._getHtmlForWebview(mermaidData);
    }

    private _getHtmlForWebview(mermaidData: string) {
        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Architecture Topology</title>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-editor-foreground);
                        background-color: var(--vscode-editor-background);
                        padding: 20px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }
                    h1 {
                        font-size: 1.5em;
                        border-bottom: 1px solid var(--vscode-panel-border);
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                        width: 100%;
                        text-align: left;
                    }
                    .mermaid {
                        background-color: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        width: 90%;
                        display: flex;
                        justify-content: center;
                    }
                </style>
            </head>
            <body>
                <h1>Architecture Topology</h1>
                <div class="mermaid">
                    ${mermaidData}
                </div>
                
                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({ startOnLoad: true, theme: 'default' });
                </script>
            </body>
            </html>`;
    }

    public dispose() {
        ArchitecturePanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) { x.dispose(); }
        }
    }
}
