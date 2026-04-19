#!/bin/bash
# Setup script for git hooks and pre-commit

set -e

echo "🔧 Setting up pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    if ! command -v uv &> /dev/null; then
        echo "❌ uv is required to install pre-commit. Install uv first: https://docs.astral.sh/uv/"
        exit 1
    fi
    echo "📦 Installing pre-commit with uv..."
    uv tool install pre-commit
fi

# Install the git hooks
echo "🪝 Installing git hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

echo "✅ Pre-commit hooks installed successfully!"
echo ""
echo "📋 Installed hooks:"
echo "  • Commit message validation (conventional commits)"
echo "  • Linting + formatting (ruff)"
echo "  • Type checking (mypy)"
echo "  • General file checks (trailing whitespace, merge conflicts, etc.)"
echo ""
echo "💡 Tips:"
echo "  • Run 'pre-commit run --all-files' to check all files"
echo "  • Run 'pre-commit run <hook-id>' to run a specific hook"
echo "  • Run 'pre-commit clean' to clean cached data"
echo "  • Add '--no-verify' to git commit to skip hooks (not recommended!)"
