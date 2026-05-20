# Contributing to InfraMind

First off, thank you for considering contributing to InfraMind! 

InfraMind is an AI-native Infrastructure Intelligence platform focused on deterministic infrastructure cognition. We welcome contributions that improve our parsing accuracy, expand our security heuristics, and optimize our VS Code extension.

## Core Philosophy

Before contributing, please review our core architectural principles:

1. **Deterministic-First**: We prefer deterministic AST parsing (e.g. `hcl2`, `pyyaml`) and hardcoded heuristics over LLM magic for baseline intelligence.
2. **Local-First Security**: Infrastructure is highly sensitive. We NEVER upload raw source code to external APIs by default. The extension processes code locally and only sends structured telemetry/summaries to the AI layer if explicitly invoked.
3. **Infrastructure Cognition**: This is not a "generic AI chatbot". It is a contextual reasoning engine that understands topologies, blast radius, and dependencies.

## Development Workflow

### 1. Backend Startup
```bash
cd apps/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Extension Compilation
```bash
cd apps/vscode-extension
npm install
npm run compile
```
Press `F5` in VS Code to launch the Extension Development Host.

### 3. Running the Regression Suite (MANDATORY)
Before opening a Pull Request, you **must** ensure that the regression suite passes. The suite acts as our quality moat to ensure parsers don't break on edge cases and false positives remain silent.

```bash
python run_tests.py
```
All pull requests must pass the CI Regression Action.

## Coding Standards

- **Python**: We use `black` for formatting and `flake8` for linting.
- **TypeScript**: We enforce strict typing. Avoid `any`.
- **UI**: Keep Webview panels clean, fast, and responsive. Skeleton loaders are preferred over blank screens.

## Submitting a Pull Request

1. Fork the repo and create your branch from `main`.
2. Ensure you have added test cases in `tests/` for any new parser logic or heuristic you introduce.
3. Ensure `python run_tests.py` passes 100%.
4. Issue that PR!
