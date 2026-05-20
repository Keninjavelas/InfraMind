import * as vscode from 'vscode';
import { getArchitectureDiagram } from '../services/api';
import { ArchitecturePanel } from '../panels/architecturePanel';

export async function visualizeArchitectureCommand(context: vscode.ExtensionContext) {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('InfraMind: Please open a workspace containing Infrastructure files.');
        return;
    }
    
    const rootPath = workspaceFolders[0].uri.fsPath;
    
    // Step 1: Show Architecture Panel immediately with Loading Skeleton
    ArchitecturePanel.createOrShow(context.extensionUri);
    if (ArchitecturePanel.currentPanel) {
        ArchitecturePanel.currentPanel.setLoading();
    }
    
    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "InfraMind: Generating Topology Diagram...",
        cancellable: false
    }, async (progress) => {
        try {
            // Step 2: Call Backend to get Diagram
            const mermaidData = await getArchitectureDiagram(rootPath);
            
            // Step 3: Send data to Webview
            if (ArchitecturePanel.currentPanel) {
                ArchitecturePanel.currentPanel.updateContent(mermaidData);
            }
            
        } catch (error: any) {
            vscode.window.showErrorMessage(`InfraMind Error: ${error.message}. Is the backend running?`);
            if (ArchitecturePanel.currentPanel) {
                ArchitecturePanel.currentPanel.setError(error.message);
            }
        }
    });
}
