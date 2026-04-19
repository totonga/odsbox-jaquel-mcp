# ODS Jaquel MCP Development Container

This devcontainer provides a fully configured Python 3.13 development environment for the ODS Jaquel MCP project.

## Features

- **Python 3.13**: Latest stable Python version specified in `pyproject.toml`
- **Git Integration**: Pre-installed for version control
- **VS Code Extensions**: Python development tools including Pylance, debugger, and Ruff formatter/linter
- **Pre-configured Environment**:
   - Project dependencies installed with uv (`uv sync --all-extras --dev`)
  - Python formatting and linting configured
  - Pytest testing configured

## Getting Started

1. **Open in Dev Container**:
   - Open the project folder in VS Code
   - Run: **Dev Containers: Reopen in Container** (Cmd/Ctrl+Shift+P)

2. **Verify Installation**:
   ```bash
   uv --version
   uv run pytest tests/ -v
   ```

3. **Run the Server**:
   ```bash
   uv run python -m odsbox_jaquel_mcp
   ```

4. **Build Package**:
   ```bash
   uv build
   ```

## Development Workflow

- **Format Code**: `uv run ruff format .` or use VS Code's Format Document
- **Lint**: `uv run ruff check .`
- **Type Check**: `mypy odsbox_jaquel_mcp/`
- **Run Tests**: Press Ctrl+Shift+D to open Test Explorer or run `uv run pytest tests/ -v`
- **Debug**: Set breakpoints and use VS Code Debugger (F5)

## SSH Access

Your local SSH keys are mounted read-only for Git authentication. This allows seamless Git operations within the container.

## Troubleshooting

- **Port Forwarding**: If connecting to ODS servers, use port forwarding in VS Code
- **Rebuild**: Close the dev container and rebuild with **Dev Containers: Rebuild Container**
