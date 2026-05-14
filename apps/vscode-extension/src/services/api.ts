import * as vscode from 'vscode';
import * as http from 'http';

export async function parseInfrastructure(directoryPath: string): Promise<any> {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify({ directory_path: directoryPath });

        const options = {
            hostname: '127.0.0.1',
            port: 8000,
            path: '/api/v1/parse',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
                    try { resolve(JSON.parse(data)); } catch(e) { reject(e); }
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

export async function getArchitectureDiagram(directoryPath: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify({ directory_path: directoryPath });

        const options = {
            hostname: '127.0.0.1',
            port: 8000,
            path: '/api/v1/diagram',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
                    try { 
                        const result = JSON.parse(data);
                        resolve(result.mermaid);
                    } catch(e) { reject(e); }
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
