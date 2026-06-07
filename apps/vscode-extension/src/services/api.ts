import * as vscode from 'vscode';
import * as https from 'https';
import * as http from 'http';
import { URL } from 'url';

export function getBackendUrl(): string {
    const config = vscode.workspace.getConfiguration("inframind");
    return config.get<string>(
        "backendUrl",
        "https://inframind-hqrl.onrender.com"
    ).replace(/\/$/, '');
}

function getAIConfig() {
    const config = vscode.workspace.getConfiguration("inframind");
    return {
        apiKey: config.get<string>("apiKey", ""),
        provider: config.get<string>("provider", "auto"),
        model: config.get<string>("model", ""),
        baseUrl: config.get<string>("ollamaHost", "http://localhost:11434")
    };
}

async function makeRequest(path: string, postData: any): Promise<string> {
    const baseUrl = getBackendUrl();
    const url = new URL(`${baseUrl}${path}`);
    const isHttps = url.protocol === 'https:';
    const requestModule = isHttps ? https : http;
    const body = JSON.stringify(postData);

    return new Promise((resolve, reject) => {
        const options = {
            hostname: url.hostname,
            port: url.port || (isHttps ? 443 : 80),
            path: url.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body)
            }
        };

        const req = requestModule.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
                    resolve(data);
                } else {
                    reject(new Error(`API Error: ${res.statusCode} - ${data}`));
                }
            });
        });

        req.on('error', (e) => reject(e));
        req.write(body);
        req.end();
    });
}

export async function parseInfrastructure(directoryPath: string): Promise<any> {
    const aiConfig = getAIConfig();
    const payload = { 
        directory_path: directoryPath,
        api_key: aiConfig.apiKey,
        provider: aiConfig.provider,
        model: aiConfig.model,
        base_url: aiConfig.baseUrl
    };
    const response = await makeRequest('/api/v1/parse', payload);
    return JSON.parse(response);
}

export async function getArchitectureDiagram(directoryPath: string): Promise<string> {
    const aiConfig = getAIConfig();
    const payload = { 
        directory_path: directoryPath,
        api_key: aiConfig.apiKey,
        provider: aiConfig.provider,
        model: aiConfig.model,
        base_url: aiConfig.baseUrl
    };
    const response = await makeRequest('/api/v1/diagram', payload);
    const result = JSON.parse(response);
    return result.mermaid;
}
