import * as vscode from 'vscode';
import { StateStore } from '../state/store';

export class InfraMindHoverProvider implements vscode.HoverProvider {
    provideHover(document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken): vscode.ProviderResult<vscode.Hover> {
        const summary = StateStore.getInfraSummary();
        if (!summary || !summary.resources) return null;

        const currentLine = position.line + 1;
        const currentFilePath = document.uri.fsPath;

        let activeResource = null;
        for (const res of summary.resources) {
            // Rough block detection: line_start to line_start + 15
            if (res.file_path === currentFilePath && currentLine >= res.line_start && currentLine <= (res.line_start + 15)) {
                activeResource = res;
                break;
            }
        }

        if (!activeResource) return null;

        // Find relationships
        const resourceId = `${activeResource.resource_type}.${activeResource.name}`;
        const connectedTo = summary.dependencies
            .filter((d: any) => d.source === resourceId || d.target === resourceId)
            .map((d: any) => d.source === resourceId ? d.target : d.source)
            .map((id: string) => {
                const depRes = summary.resources.find((r: any) => `${r.resource_type}.${r.name}` === id);
                return depRes ? depRes.service_name : id;
            });

        const uniqueConnections = [...new Set(connectedTo)];
        const risks = summary.security_risks.filter((r: any) => r.resource_id === resourceId);

        // Build Markdown
        const md = new vscode.MarkdownString();
        md.isTrusted = true;

        md.appendMarkdown(`### 🧠 InfraMind Intelligence\n`);
        md.appendMarkdown(`**Service:** \`${activeResource.service_name}\` | **Provider:** \`${activeResource.provider}\`\n\n`);

        if (risks.length > 0) {
            md.appendMarkdown(`---\n#### 🚨 Detected Risks\n`);
            risks.forEach((r: any) => {
                const icon = r.severity === 'CRITICAL' ? '🔴' : r.severity === 'HIGH' ? '🟠' : '🟡';
                md.appendMarkdown(`${icon} **${r.severity} (${r.category})**: ${r.description}\n`);
                md.appendMarkdown(`*Recommendation:* ${r.recommendation}\n\n`);
            });
        }

        if (uniqueConnections.length > 0) {
            md.appendMarkdown(`---\n#### 🔗 Connected To\n`);
            uniqueConnections.forEach((conn: any) => {
                md.appendMarkdown(`- \`${conn}\`\n`);
            });
            md.appendMarkdown(`\n`);
        }

        md.appendMarkdown(`---\n[✨ Ask AI to Explain](command:inframind.explainResource)`);

        return new vscode.Hover(md);
    }
}
