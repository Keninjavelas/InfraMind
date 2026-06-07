import * as vscode from 'vscode';
import { analyzeWorkspaceCommand } from './commands/analyze';
import { visualizeArchitectureCommand } from './commands/visualize';
import { InfraMindDiagnostics } from './diagnostics';
import { InfraMindHoverProvider } from './hover/provider';
import { SettingsPanel } from './panels/settingsPanel';
import { SidebarProvider } from './panels/sidebarProvider';

export function activate(context: vscode.ExtensionContext) {
	console.log('InfraMind extension is now active!');

	const diagnosticsEngine = new InfraMindDiagnostics();
	context.subscriptions.push(diagnosticsEngine);

    // Sidebar Providers
    const securityProvider = new SidebarProvider('security');
    const architectureProvider = new SidebarProvider('architecture');
    const actionsProvider = new SidebarProvider('actions');

    vscode.window.registerTreeDataProvider('inframind.securityView', securityProvider);
    vscode.window.registerTreeDataProvider('inframind.architectureView', architectureProvider);
    vscode.window.registerTreeDataProvider('inframind.actionsView', actionsProvider);

	vscode.workspace.onDidSaveTextDocument(document => {
		diagnosticsEngine.updateDiagnostics(document).then(() => {
            securityProvider.refresh();
        });
	});

    if (vscode.window.activeTextEditor) {
        diagnosticsEngine.updateDiagnostics(vscode.window.activeTextEditor.document).then(() => {
            securityProvider.refresh();
        });
    }

    // Commands
    let refreshSidebarDisposable = vscode.commands.registerCommand('inframind.refreshSidebar', () => {
        securityProvider.refresh();
        architectureProvider.refresh();
        actionsProvider.refresh();
    });

	let analyzeDisposable = vscode.commands.registerCommand('inframind.analyzeWorkspace', async () => {
		await analyzeWorkspaceCommand(context);
        securityProvider.refresh();
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
    context.subscriptions.push(refreshSidebarDisposable);
    context.subscriptions.push(explainDisposable);

    // Register Hover
    const hoverProvider = vscode.languages.registerHoverProvider('terraform', new InfraMindHoverProvider());
    context.subscriptions.push(hoverProvider);
}

export function deactivate() {}
