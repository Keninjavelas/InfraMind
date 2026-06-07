import * as vscode from 'vscode';
import { analyzeWorkspaceCommand } from './commands/analyze';
import { visualizeArchitectureCommand } from './commands/visualize';
import { InfraMindDiagnostics } from './diagnostics';
import { InfraMindHoverProvider } from './hover/provider';
import { SettingsPanel } from './panels/settingsPanel';

export function activate(context: vscode.ExtensionContext) {
	console.log('InfraMind extension is now active!');

	const diagnosticsEngine = new InfraMindDiagnostics();
	context.subscriptions.push(diagnosticsEngine);

	vscode.workspace.onDidSaveTextDocument(document => {
		diagnosticsEngine.updateDiagnostics(document);
	});

    if (vscode.window.activeTextEditor) {
        diagnosticsEngine.updateDiagnostics(vscode.window.activeTextEditor.document);
    }

    // Register Hover
    const hoverProvider = vscode.languages.registerHoverProvider('terraform', new InfraMindHoverProvider());
    context.subscriptions.push(hoverProvider);

	let analyzeDisposable = vscode.commands.registerCommand('inframind.analyzeWorkspace', () => {
		analyzeWorkspaceCommand(context);
	});

	let visualizeDisposable = vscode.commands.registerCommand('inframind.visualizeArchitecture', () => {
		visualizeArchitectureCommand(context);
	});

    let settingsDisposable = vscode.commands.registerCommand('inframind.openSettings', () => {
        SettingsPanel.render(context.extensionUri);
    });

    let explainDisposable = vscode.commands.registerCommand('inframind.explainResource', () => {
		vscode.window.showInformationMessage("InfraMind AI: This resource is part of the core infrastructure. AI deep-dive coming in the next update!");
	});

	context.subscriptions.push(analyzeDisposable);
	context.subscriptions.push(visualizeDisposable);
    context.subscriptions.push(settingsDisposable);
    context.subscriptions.push(explainDisposable);
}

export function deactivate() {}
