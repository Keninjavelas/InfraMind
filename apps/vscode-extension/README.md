# InfraMind

AI-native Infrastructure Intelligence for Terraform, Kubernetes, and Docker.

InfraMind is not a generic AI assistant. It is a **deterministic infrastructure cognition engine**. 

We parse Terraform, Kubernetes, and Docker locally to build a semantic graph of your infrastructure. This local-first security model ensures your raw infrastructure code never leaves your machine. We only use AI reasoning as an optional, high-leverage layer on top of our structured intelligence.

## Core Features

### 🏗️ Terraform Intelligence
- **Semantic Parsing:** High-fidelity HCL parsing and state extraction.
- **Diagnostics:** Real-time, inline security and complexity validation.
- **Topology Visualization:** Automatic blast-radius mapping for AWS resources.

### ☸️ Kubernetes Intelligence
- **Workload Mapping:** Deep dependency linking between Ingresses, Services, and Deployments.
- **Security Heuristics:** Pinpoint privileged execution, root escalation, and plaintext secrets.
- **Dependency Graphing:** Visual representations of your cluster architecture.

### 🐋 Docker Intelligence
- **Compose Topology:** Deterministic mapping of inter-service network boundaries.
- **Privileged Detection:** Immediate flagging of dangerous host-level escalations.
- **Container Security Analysis:** Dockerfile deep-dives for dangerous package and user specs.

### ⚡ VS Code UX
- **Inline Diagnostics:** Immediate feedback loops powered by debounced local parsing.
- **Hover Intelligence:** Context-aware infrastructure data on hover.
- **Topology Graphs:** Interactive Mermaid diagrams rendered natively in Webviews.
- **Deterministic Responsiveness:** Lightning-fast UI, powered by local evaluation.

## Requirements

- VS Code v1.80+
- Access to the InfraMind backend (configured via settings)

## Extension Settings

- `inframind.backendUrl`: The URL of the InfraMind backend service.
- `inframind.provider`: The AI provider to use for explanations and reviews (default: `groq`).
- `inframind.apiKey`: User-supplied API Key for AI operations (overrides server-side keys).

## License

MIT
