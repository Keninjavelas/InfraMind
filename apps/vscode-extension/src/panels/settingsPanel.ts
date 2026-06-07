import * as vscode from 'vscode';
import { getBackendUrl } from '../services/api';

export class SettingsPanel {
    public static currentPanel: SettingsPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.webview.html = this._getWebviewContent();
        this._setWebviewMessageListener(this._panel.webview);
    }

    public static render(extensionUri: vscode.Uri) {
        if (SettingsPanel.currentPanel) {
            SettingsPanel.currentPanel._panel.reveal(vscode.ViewColumn.One);
        } else {
            const panel = vscode.window.createWebviewPanel(
                "inframindSettings",
                "InfraMind Settings",
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                }
            );

            SettingsPanel.currentPanel = new SettingsPanel(panel, extensionUri);
        }
    }

    public dispose() {
        SettingsPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _getWebviewContent() {
        const config = vscode.workspace.getConfiguration("inframind");
        const backendUrl = config.get<string>("backendUrl", "https://inframind-hqrl.onrender.com");
        const provider = config.get<string>("provider", "groq");
        const apiKey = config.get<string>("apiKey", "");

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>InfraMind Settings</title>
            <style>
                body { font-family: var(--vscode-font-family); color: var(--vscode-foreground); padding: 20px; line-height: 1.6; }
                .container { max-width: 600px; margin: 0 auto; }
                .section { margin-bottom: 25px; padding: 15px; border: 1px solid var(--vscode-panel-border); border-radius: 4px; }
                .section-title { font-weight: bold; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
                .form-group { margin-bottom: 15px; }
                label { display: block; margin-bottom: 5px; font-size: 0.9em; opacity: 0.8; }
                input, select { width: 100%; padding: 8px; box-sizing: border-box; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); border-radius: 2px; }
                .button-group { display: flex; gap: 10px; margin-top: 20px; }
                button { padding: 8px 16px; cursor: pointer; background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 2px; }
                button:hover { background: var(--vscode-button-hoverBackground); }
                button.secondary { background: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground); }
                button.secondary:hover { background: var(--vscode-button-secondaryHoverBackground); }
                .status { margin-top: 10px; font-size: 0.9em; padding: 8px; border-radius: 2px; display: none; }
                .status.success { display: block; background: rgba(74, 161, 101, 0.2); color: #4aa165; border: 1px solid #4aa165; }
                .status.error { display: block; background: rgba(241, 76, 76, 0.2); color: #f14c4c; border: 1px solid #f14c4c; }
                .about { text-align: center; margin-top: 40px; opacity: 0.7; font-size: 0.85em; }
                .creator { font-weight: bold; color: var(--vscode-textLink-foreground); }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>InfraMind Settings</h2>
                
                <div class="section">
                    <div class="section-title">Backend Configuration</div>
                    <div class="form-group">
                        <label for="backendUrl">Backend URL</label>
                        <input type="text" id="backendUrl" value="${backendUrl}" placeholder="https://inframind-hqrl.onrender.com">
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">AI Reasoning Layer</div>
                    <div class="form-group">
                        <label for="provider">AI Provider</label>
                        <select id="provider">
                            <option value="groq" ${provider === 'groq' ? 'selected' : ''}>Groq (Fastest)</option>
                            <option value="openai" ${provider === 'openai' ? 'selected' : ''}>OpenAI (Coming Soon)</option>
                            <option value="gemini" ${provider === 'gemini' ? 'selected' : ''}>Gemini (Coming Soon)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="apiKey">Groq API Key</label>
                        <input type="password" id="apiKey" value="${apiKey}" placeholder="Enter your gsk_...">
                    </div>
                </div>

                <div class="button-group">
                    <button id="saveBtn">Save Settings</button>
                    <button id="testBtn" class="secondary">Test Connection</button>
                </div>

                <div id="status" class="status"></div>

                <div class="about">
                    <div>InfraMind v0.1.0</div>
                    <div>Created by <span class="creator">Aryan Kapoor / Keninjavelas</span></div>
                    <div style="margin-top: 8px;">
                        <a href="https://github.com/Keninjavelas/InfraMind" style="color: var(--vscode-textLink-foreground); text-decoration: none;">GitHub Repository</a>
                    </div>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                const saveBtn = document.getElementById('saveBtn');
                const testBtn = document.getElementById('testBtn');
                const statusDiv = document.getElementById('status');

                saveBtn.addEventListener('click', () => {
                    const backendUrl = document.getElementById('backendUrl').value;
                    const provider = document.getElementById('provider').value;
                    const apiKey = document.getElementById('apiKey').value;

                    vscode.postMessage({
                        command: 'save',
                        settings: { backendUrl, provider, apiKey }
                    });
                });

                testBtn.addEventListener('click', () => {
                    const backendUrl = document.getElementById('backendUrl').value;
                    const apiKey = document.getElementById('apiKey').value;
                    
                    statusDiv.className = 'status';
                    statusDiv.textContent = 'Testing connection...';
                    statusDiv.style.display = 'block';

                    vscode.postMessage({
                        command: 'test',
                        settings: { backendUrl, apiKey }
                    });
                });

                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.command === 'status') {
                        statusDiv.className = 'status ' + message.type;
                        statusDiv.textContent = message.text;
                    }
                });
            </script>
        </body>
        </html>`;
    }

    private _setWebviewMessageListener(webview: vscode.Webview) {
        webview.onDidReceiveMessage(
            async (message) => {
                const { command, settings } = message;

                switch (command) {
                    case "save":
                        const config = vscode.workspace.getConfiguration("inframind");
                        await config.update("backendUrl", settings.backendUrl, vscode.ConfigurationTarget.Global);
                        await config.update("provider", settings.provider, vscode.ConfigurationTarget.Global);
                        await config.update("apiKey", settings.apiKey, vscode.ConfigurationTarget.Global);
                        
                        webview.postMessage({
                            command: 'status',
                            type: 'success',
                            text: '✓ Settings saved successfully'
                        });
                        break;

                    case "test":
                        try {
                            // Simple health check call
                            const controller = new AbortController();
                            const timeoutId = setTimeout(() => controller.abort(), 5000);
                            
                            const response = await fetch(`${settings.backendUrl}/api/v1/health`, {
                                signal: controller.signal
                            });
                            
                            clearTimeout(timeoutId);

                            if (response.ok) {
                                webview.postMessage({
                                    command: 'status',
                                    type: 'success',
                                    text: '✓ Connected to backend successfully'
                                });
                            } else {
                                throw new Error(`HTTP ${response.status}`);
                            }
                        } catch (e) {
                            webview.postMessage({
                                command: 'status',
                                type: 'error',
                                text: `✗ Connection failed: ${e instanceof Error ? e.message : 'Unknown error'}`
                            });
                        }
                        break;
                }
            },
            undefined,
            this._disposables
        );
    }
}
