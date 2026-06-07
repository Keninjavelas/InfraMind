import * as vscode from 'vscode';
import { StateStore } from '../state/store';

export class SidebarProvider implements vscode.TreeDataProvider<InfraItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<InfraItem | undefined | null | void> = new vscode.EventEmitter<InfraItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<InfraItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private viewType: 'security' | 'architecture' | 'actions') {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: InfraItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: InfraItem): Promise<InfraItem[]> {
        const summary = StateStore.getInfraSummary();
        
        if (this.viewType === 'security') {
            if (!summary || !summary.security_risks) {
                return [new InfraItem("No risks detected", vscode.TreeItemCollapsibleState.None, "check")];
            }
            return summary.security_risks.map((risk: any) => {
                const item = new InfraItem(
                    risk.description,
                    vscode.TreeItemCollapsibleState.None,
                    this.getSeverityIcon(risk.severity),
                    {
                        command: 'vscode.open',
                        title: 'Open File',
                        arguments: [
                            vscode.Uri.file(risk.file_path),
                            { selection: new vscode.Range(risk.line_number - 1, 0, risk.line_number - 1, 0) }
                        ]
                    }
                );
                item.tooltip = `${risk.category}: ${risk.recommendation}`;
                return item;
            });
        }

        if (this.viewType === 'architecture') {
            return [
                new InfraItem("Open Topology Diagram", vscode.TreeItemCollapsibleState.None, "graph", {
                    command: 'inframind.visualizeArchitecture',
                    title: 'Visualize Architecture'
                }),
                new InfraItem("Resource Inventory", vscode.TreeItemCollapsibleState.None, "list-unordered")
            ];
        }

        if (this.viewType === 'actions') {
            return [
                new InfraItem("Analyze Workspace", vscode.TreeItemCollapsibleState.None, "play", {
                    command: 'inframind.analyzeWorkspace',
                    title: 'Analyze Workspace'
                }),
                new InfraItem("Open Settings", vscode.TreeItemCollapsibleState.None, "settings-gear", {
                    command: 'inframind.openSettings',
                    title: 'Open Settings'
                }),
                new InfraItem("InfraMind Documentation", vscode.TreeItemCollapsibleState.None, "book", {
                    command: 'vscode.open',
                    title: 'Open Docs',
                    arguments: [vscode.Uri.parse('https://github.com/Keninjavelas/InfraMind')]
                })
            ];
        }

        return [];
    }

    private getSeverityIcon(severity: string): string {
        switch (severity) {
            case 'CRITICAL': return 'error';
            case 'HIGH': return 'warning';
            case 'MEDIUM': return 'info';
            default: return 'issues';
        }
    }
}

class InfraItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly iconName?: string,
        public readonly command?: vscode.Command
    ) {
        super(label, collapsibleState);
        if (iconName) {
            this.iconPath = new vscode.ThemeIcon(iconName);
        }
    }
}
