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
        const provider = config.get<string>("provider", "auto");
        const apiKey = config.get<string>("apiKey", "");
        const model = config.get<string>("model", "");
        const ollamaHost = config.get<string>("ollamaHost", "http://localhost:11434");

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
                .form-group.hidden { display: none; }
                label { display: block; margin-bottom: 5px; font-size: 0.9em; opacity: 0.8; }
                input, select { width: 100%; padding: 8px; box-sizing: border-box; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); border-radius: 2px; }
                input:focus, select:focus { border-color: var(--vscode-focusBorder); outline: none; }
                option { background: var(--vscode-dropdown-background); color: var(--vscode-dropdown-foreground); }
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
                .hint { font-size: 0.8em; opacity: 0.6; margin-top: 4px; }
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
                            <option value="auto" ${provider === 'auto' ? 'selected' : ''}>Auto-detect (Recommended)</option>
                            <option value="groq" ${provider === 'groq' ? 'selected' : ''}>Groq</option>
                            <option value="openai" ${provider === 'openai' ? 'selected' : ''}>OpenAI</option>
                            <option value="anthropic" ${provider === 'anthropic' ? 'selected' : ''}>Anthropic</option>
                            <option value="gemini" ${provider === 'gemini' ? 'selected' : ''}>Gemini</option>
                            <option value="openrouter" ${provider === 'openrouter' ? 'selected' : ''}>OpenRouter</option>
                            <option value="ollama" ${provider === 'ollama' ? 'selected' : ''}>Ollama (Local)</option>
                        </select>
                        <div class="hint" id="providerHint">Auto-detects provider based on your API key format.</div>
                    </div>

                    <div class="form-group" id="apiKeyGroup">
                        <label id="apiKeyLabel" for="apiKey">API Key</label>
                        <input type="password" id="apiKey" value="${apiKey}" placeholder="Enter your API key...">
                    </div>

                    <div class="form-group hidden" id="modelGroup">
                        <label for="model">Model Name</label>
                        <input type="text" id="model" value="${model}" placeholder="e.g. gpt-4o, claude-3-5-sonnet, llama3">
                    </div>

                    <div class="form-group hidden" id="ollamaHostGroup">
                        <label for="ollamaHost">Ollama Host</label>
                        <input type="text" id="ollamaHost" value="${ollamaHost}" placeholder="http://localhost:11434">
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
                    <div style="margin-top: 12px; display: flex; justify-content: center; gap: 15px;">
                        <a href="https://infra-site-three.vercel.app/" style="color: var(--vscode-textLink-foreground); text-decoration: none;">Website</a>
                        <a href="https://marketplace.visualstudio.com/items?itemName=aryankapoor-keninjavelas.inframind" style="color: var(--vscode-textLink-foreground); text-decoration: none;">Marketplace</a>
                        <a href="https://github.com/Keninjavelas/InfraMind" style="color: var(--vscode-textLink-foreground); text-decoration: none;">GitHub</a>
                    </div>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                const providerSelect = document.getElementById('provider');
                const apiKeyGroup = document.getElementById('apiKeyGroup');
                const modelGroup = document.getElementById('modelGroup');
                const ollamaHostGroup = document.getElementById('ollamaHostGroup');
                const providerHint = document.getElementById('providerHint');
                const apiKeyLabel = document.getElementById('apiKeyLabel');

                function updateUI() {
                    const provider = providerSelect.value;
                    
                    // Default visibility
                    apiKeyGroup.classList.remove('hidden');
                    modelGroup.classList.add('hidden');
                    ollamaHostGroup.classList.add('hidden');
                    providerHint.style.display = 'none';
                    apiKeyLabel.textContent = 'API Key';

                    if (provider === 'auto') {
                        providerHint.style.display = 'block';
                        providerHint.textContent = 'Auto-detects provider (Groq, OpenAI, Anthropic) based on API key format.';
                    } else if (provider === 'ollama') {
                        apiKeyGroup.classList.add('hidden');
                        modelGroup.classList.remove('hidden');
                        ollamaHostGroup.classList.remove('hidden');
                    } else if (provider === 'groq') {
                        apiKeyLabel.textContent = 'Groq API Key';
                    } else if (provider === 'openai') {
                        apiKeyLabel.textContent = 'OpenAI API Key';
                        modelGroup.classList.remove('hidden');
                    } else if (provider === 'anthropic') {
                        apiKeyLabel.textContent = 'Anthropic API Key';
                        modelGroup.classList.remove('hidden');
                    } else if (provider === 'gemini') {
                        apiKeyLabel.textContent = 'Gemini API Key';
                        modelGroup.classList.remove('hidden');
                    } else if (provider === 'openrouter') {
                        apiKeyLabel.textContent = 'OpenRouter API Key';
                        modelGroup.classList.remove('hidden');
                    }
                }

                providerSelect.addEventListener('change', updateUI);
                updateUI(); // Initial call

                document.getElementById('saveBtn').addEventListener('click', () => {
                    vscode.postMessage({
                        command: 'save',
                        settings: { 
                            backendUrl: document.getElementById('backendUrl').value,
                            provider: providerSelect.value,
                            apiKey: document.getElementById('apiKey').value,
                            model: document.getElementById('model').value,
                            ollamaHost: document.getElementById('ollamaHost').value
                        }
                    });
                });

                document.getElementById('testBtn').addEventListener('click', () => {
                    const statusDiv = document.getElementById('status');
                    statusDiv.className = 'status';
                    statusDiv.textContent = 'Testing connection...';
                    statusDiv.style.display = 'block';

                    vscode.postMessage({
                        command: 'test',
                        settings: { 
                            backendUrl: document.getElementById('backendUrl').value,
                            apiKey: document.getElementById('apiKey').value
                        }
                    });
                });

                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.command === 'status') {
                        const statusDiv = document.getElementById('status');
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
                        await config.update("model", settings.model, vscode.ConfigurationTarget.Global);
                        await config.update("ollamaHost", settings.ollamaHost, vscode.ConfigurationTarget.Global);
                        
                        webview.postMessage({
                            command: 'status',
                            type: 'success',
                            text: '✓ Settings saved successfully'
                        });
                        break;

                    case "test":
                        try {
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
