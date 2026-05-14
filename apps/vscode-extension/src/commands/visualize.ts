import * as vscode from 'vscode';
import { getArchitectureDiagram } from '../services/api';
import { ArchitecturePanel } from '../panels/architecturePanel';

export async function visualizeArchitectureCommand(context: vscode.ExtensionContext) {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('InfraMind: Please open a workspace containing Terraform files.');
        return;
    }
    
    const rootPath = workspaceFolders[0].uri.fsPath;
    
    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "InfraMind: Generating Topology Diagram...",
        cancellable: false
    }, async (progress) => {
        try {
            // Step 1: Call Backend to get Diagram
            const mermaidData = await getArchitectureDiagram(rootPath);
            
            // Step 2: Show Architecture Panel
            ArchitecturePanel.createOrShow(context.extensionUri);
            
            // Step 3: Send data to Webview
            if (ArchitecturePanel.currentPanel) {
                ArchitecturePanel.currentPanel.updateContent(mermaidData);
            }
            
        } catch (error: any) {
            vscode.window.showErrorMessage(`InfraMind Error: ${error.message}. Is the backend running?`);
        }
    });
}
