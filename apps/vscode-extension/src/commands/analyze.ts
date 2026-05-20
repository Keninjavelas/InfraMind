import * as vscode from 'vscode';
import { parseInfrastructure } from '../services/api';
import { SecurityPanel } from '../panels/securityPanel';

export async function analyzeWorkspaceCommand(context: vscode.ExtensionContext) {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('InfraMind: Please open a workspace containing Infrastructure files.');
        return;
    }
    
    const rootPath = workspaceFolders[0].uri.fsPath;
    
    // Step 1: Show Security Panel immediately with Loading Skeleton
    SecurityPanel.createOrShow(context.extensionUri);
    if (SecurityPanel.currentPanel) {
        SecurityPanel.currentPanel.setLoading();
    }
    
    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "InfraMind: Analyzing Infrastructure Context...",
        cancellable: false
    }, async (progress) => {
        try {
            // Step 2: Call Backend to get Structured Intelligence
            const infraSummary = await parseInfrastructure(rootPath);
            
            // Step 3: Send data to Webview
            if (SecurityPanel.currentPanel) {
                SecurityPanel.currentPanel.updateContent(infraSummary);
            }
            
            vscode.window.showInformationMessage('InfraMind: Analysis complete!');
        } catch (error: any) {
            vscode.window.showErrorMessage(`InfraMind Error: ${error.message}. Is the backend running?`);
        }
    });
}
