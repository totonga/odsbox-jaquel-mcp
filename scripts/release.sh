#!/bin/bash
set -e

# Simple release helper script for odsbox-jaquel-mcp
# Usage: ./scripts/release.sh [major|minor|patch]
# Default: patch

RELEASE_TYPE=${1:-patch}

if [[ ! "$RELEASE_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "Usage: $0 [major|minor|patch]"
    echo "Default: patch"
    exit 1
fi

echo "🚀 Starting $RELEASE_TYPE release..."

# Check if repo is clean
if ! git diff --quiet; then
    echo "❌ Git working directory is not clean. Please commit or stash changes."
    exit 1
fi

# Ensure on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Not on main branch. Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Run tests
echo "🧪 Running tests..."
uv run pytest tests/ -v --tb=short || exit 1

# Install semantic-release if not available
if ! command -v semantic-release &> /dev/null; then
    echo "📦 Installing python-semantic-release with uv..."
    uv tool install python-semantic-release
fi

# Create release
echo "🔖 Creating $RELEASE_TYPE release..."
git config user.email "$(git config user.email || echo 'github-actions@github.com')"
git config user.name "$(git config user.name || echo 'Release Bot')"

# Use semantic-release
semantic-release publish --ci

echo "✅ Release complete!"
echo "📋 Check GitHub for new release: https://github.com/totonga/odsbox-jaquel-mcp/releases"
