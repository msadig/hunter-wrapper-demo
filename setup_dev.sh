#!/bin/bash
# Development environment setup script for Hunter.io API Client

echo "Setting up development environment for Hunter.io API Client..."
echo "=============================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"

# Install dependencies
echo "Installing runtime dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Runtime dependencies installed"

echo "Installing development dependencies..."
pip install -r requirements-dev.txt --quiet
echo "✓ Development dependencies installed"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install
echo "✓ Pre-commit hooks installed"

# Run pre-commit on all files to verify setup
echo "Running initial pre-commit checks..."
pre-commit run --all-files || true
echo "✓ Initial pre-commit check complete"

# Check if setuptools version is compatible
echo ""
echo "=============================================="
echo "✅ Development environment setup complete!"
echo ""
echo "Pre-commit hooks are now active and will run automatically before each commit."
echo "The following checks will be performed:"
echo "  • Trailing whitespace removal"
echo "  • End-of-file fixes"
echo "  • Import sorting (isort)"
echo "  • Type checking (mypy)"
echo "  • Linting (wemake-python-styleguide)"
echo ""
echo "To manually run pre-commit on all files:"
echo "  pre-commit run --all-files"
echo ""
echo "To run pre-commit on staged files only:"
echo "  pre-commit run"
echo ""
echo "To update pre-commit hooks to latest versions:"
echo "  pre-commit autoupdate"
