import * as vscode from 'vscode';
import { parseInfrastructure } from './services/api';
import { StateStore } from './state/store';

export class InfraMindDiagnostics {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private debounceTimer: NodeJS.Timeout | null = null;

    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('inframind');
    }

    public async updateDiagnostics(document: vscode.TextDocument) {
        if (!document.fileName.endsWith('.tf') && !document.fileName.endsWith('.yaml') && !document.fileName.endsWith('.yml') && !document.fileName.includes('Dockerfile')) {
            return;
        }

        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        this.debounceTimer = setTimeout(async () => {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders) return;
            const rootPath = workspaceFolders[0].uri.fsPath;

            try {
                // Trigger lightweight local parser
                const infraSummary = await parseInfrastructure(rootPath);
                StateStore.setInfraSummary(infraSummary); // Save for Hover provider

                this.diagnosticCollection.clear();
                
                const diagnosticsMap = new Map<string, vscode.Diagnostic[]>();

                if (infraSummary.security_risks) {
                    for (const risk of infraSummary.security_risks) {
                        if (risk.file_path && risk.line_number) {
                            const fileUri = vscode.Uri.file(risk.file_path);
                            const uriStr = fileUri.toString();
                            
                            // Parse severity
                            let vscodeSeverity = vscode.DiagnosticSeverity.Information;
                            if (risk.severity === 'CRITICAL') vscodeSeverity = vscode.DiagnosticSeverity.Error;
                            else if (risk.severity === 'HIGH') vscodeSeverity = vscode.DiagnosticSeverity.Warning;
                            else if (risk.severity === 'MEDIUM') vscodeSeverity = vscode.DiagnosticSeverity.Information;
                            else if (risk.severity === 'LOW') vscodeSeverity = vscode.DiagnosticSeverity.Hint;

                            // Create Range for the diagnostic (VS Code lines are 0-indexed)
                            const line = risk.line_number - 1;
                            const range = new vscode.Range(line, 0, line, 100);
                            
                            const diagnostic = new vscode.Diagnostic(
                                range,
                                `[InfraMind] ${risk.category.toUpperCase()} RISK: ${risk.description}\nRecommended: ${risk.recommendation}`,
                                vscodeSeverity
                            );
                            diagnostic.source = 'inframind';

                            if (!diagnosticsMap.has(uriStr)) {
                                diagnosticsMap.set(uriStr, []);
                            }
                            diagnosticsMap.get(uriStr)!.push(diagnostic);
                        }
                    }
                }

                // Set all diagnostics
                for (const [uriStr, diagnostics] of diagnosticsMap.entries()) {
                    this.diagnosticCollection.set(vscode.Uri.parse(uriStr), diagnostics);
                }

            } catch (e) {
                console.error('InfraMind Diagnostics Error:', e);
            }
        }, 1000); // 1s debounce
    }

    public dispose() {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        this.diagnosticCollection.clear();
        this.diagnosticCollection.dispose();
    }
}
