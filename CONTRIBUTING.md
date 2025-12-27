# Development Setup Guide

This guide explains how to set up your development environment for contributing to odsbox-jaquel-mcp.

## Quick Start

### 1. Install Dependencies

```bash
pip install -e '.[dev]'
```

### 2. Setup Git Hooks (Recommended)

```bash
./scripts/setup-hooks.sh
```

Or manually:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

## Pre-Commit Hooks

Pre-commit hooks automatically validate your code before each commit. This ensures all code meets quality standards.

### ✅ What Gets Checked

| Hook | Purpose | What It Does |
|------|---------|--------------|
| **commitlint** | Commit messages | Enforces conventional commit format (feat:, fix:, etc.) |
| **black** | Code formatting | Auto-formats Python code to consistent style |
| **isort** | Import sorting | Sorts imports alphabetically and by type |
| **flake8** | Code style | Checks for PEP 8 violations and common errors |
| **mypy** | Type checking | Validates Python type hints |
| **trailing-whitespace** | File cleanup | Removes trailing spaces |
| **end-of-file-fixer** | File cleanup | Ensures files end with newline |
| **check-yaml** | YAML validation | Validates YAML syntax |
| **check-json** | JSON validation | Validates JSON syntax |
| **check-merge-conflict** | Git state | Detects unresolved merge conflicts |
| **debug-statements** | Code quality | Finds leftover `pdb` or `breakpoint()` calls |
| **detect-private-key** | Security | Prevents committing private keys |

### 🚀 Usage

#### First Time Setup (Automatic in Dev Container)
Pre-commit hooks are **automatically installed** when you open this workspace in a dev container.

To manually install:
```bash
# Install hooks into your local git repository
./scripts/setup-hooks.sh
# or
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg
```

#### Running Checks
```bash
# Check all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run mypy --all-files

# Run on changed files only (what happens at commit)
pre-commit run
```

#### Skipping Hooks (Not Recommended)
```bash
# Skip all hooks for a commit
git commit --no-verify

# Skip specific hooks by setting environment variable
SKIP=mypy git commit -m "feat: add new feature"
```

#### Clean Cache
```bash
pre-commit clean
```

## Conventional Commit Format

All commits must follow the conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Valid Types
- **feat** - A new feature
- **fix** - A bug fix
- **docs** - Documentation only changes
- **style** - Changes that don't affect code meaning (formatting, etc.)
- **refactor** - Code change that neither fixes a bug nor adds a feature
- **perf** - Code change that improves performance
- **test** - Adding or updating tests
- **chore** - Changes to build process, dependencies, etc.
- **ci** - Changes to CI/CD configuration
- **revert** - Revert a previous commit

### Examples

```bash
# Feature
git commit -m "feat: add data export functionality"

# Bug fix
git commit -m "fix: resolve connection timeout on large datasets"

# With scope
git commit -m "feat(submatrix): add bulk data reader"

# Multi-line
git commit -m "feat: add new measurement comparison feature

This adds support for statistical analysis of multiple measurements
and generates comparison plots automatically."
```

## Release Process

### Automatic Releases (from main branch)

Releases are triggered automatically when commits are pushed to `main`:

1. **Commit to develop/feature branch** with conventional messages
2. **Create Pull Request** to main
3. **Merge PR** to main
4. **GitHub Actions** automatically:
   - Analyzes commits
   - Bumps version (major/minor/patch)
   - Generates CHANGELOG.md
   - Creates git tag and GitHub release
   - Publishes to PyPI
   - Updates MCP Registry

### Manual Release (if needed)

```bash
./scripts/release.sh patch   # or minor/major
```

## Contributing Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature develop
   ```

2. **Make changes with conventional commits**
   ```bash
   git commit -m "feat: add my new feature"
   ```

3. **Pre-commit hooks run automatically**
   - Validates commit message
   - Formats code (black, isort)
   - Checks code quality (flake8, mypy)
   - Detects common issues

4. **Push and create PR**
   ```bash
   git push origin feature/my-feature
   ```

5. **PR validation** (GitHub Actions)
   - Runs full test suite
   - Validates commit messages
   - Checks code quality
   - Verifies no conflicts

6. **Review and merge to main**
   - Automatic release triggered

## Troubleshooting

### Pre-commit hooks not running
```bash
# Reinstall hooks
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg
```

### Black/isort formatting conflicts with editor
```bash
# These are configured in pyproject.toml:
[tool.black]
line-length = 119
target-version = ["py313"]

[tool.isort]
profile = "black"
line_length = 119
```

### Commit rejected by commitlint
Check that your commit message starts with a valid prefix:
```bash
# ❌ Wrong
git commit -m "added new feature"

# ✅ Correct
git commit -m "feat: add new feature"
```

### My commit message is too long
```
Header must be ≤ 100 characters (including prefix)

# ❌ Too long (103 chars)
git commit -m "feat: add very long commit message that exceeds the maximum allowed header length"

# ✅ Correct
git commit -m "feat: add new measurement feature"
```

### Skip mypy for a commit
```bash
SKIP=mypy git commit -m "feat: new feature"
```

## CI/CD Status

When you push to a branch with a pull request, GitHub Actions automatically:

1. ✅ Runs pytest test suite
2. ✅ Validates commit messages  
3. ✅ Checks Python code quality
4. ✅ Builds the package

See `.github/workflows/` for more details.

## Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Pre-commit Framework](https://pre-commit.com/)
- [Python Semantic Release](https://python-semantic-release.readthedocs.io/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [isort Import Sorter](https://pycqa.github.io/isort/)
