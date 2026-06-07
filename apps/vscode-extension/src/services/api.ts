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

async function makeRequest(path: string, postData: string): Promise<string> {
    const baseUrl = getBackendUrl();
    const url = new URL(`${baseUrl}${path}`);
    const isHttps = url.protocol === 'https:';
    const requestModule = isHttps ? https : http;

    return new Promise((resolve, reject) => {
        const options = {
            hostname: url.hostname,
            port: url.port || (isHttps ? 443 : 80),
            path: url.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
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
        req.write(postData);
        req.end();
    });
}

export async function parseInfrastructure(directoryPath: string): Promise<any> {
    const postData = JSON.stringify({ directory_path: directoryPath });
    const response = await makeRequest('/api/v1/parse', postData);
    return JSON.parse(response);
}

export async function getArchitectureDiagram(directoryPath: string): Promise<string> {
    const postData = JSON.stringify({ directory_path: directoryPath });
    const response = await makeRequest('/api/v1/diagram', postData);
    const result = JSON.parse(response);
    return result.mermaid;
}
