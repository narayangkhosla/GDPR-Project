#!/bin/bash

# Assumes .venv is already created and activated
# This purpose of this file is to:
# Install all dependencies
# Make helper scripts executable
# Verify that LocalStack is running

set -e  # Exit on error

echo "� Checking if a virtual environment is active..."

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ No active virtual environment detected."
    echo "   Please activate your virtual environment before running this script."
    echo "   For example: source .venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment is active: $VIRTUAL_ENV"
echo "   Python: $(which python)"
echo "   Version: $(python --version)"

echo "� Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "� Making helper scripts executable..."
chmod +x create_test_data.sh run_test_data.sh run-pytest-mac.sh check_pep8.sh

echo "-------------------------"
echo "� Checking LocalStack setup..."

# 1. Check if Docker-based LocalStack is running
if docker ps | grep -q localstack; then
    echo "✅ LocalStack Docker container is running."
else
    echo "⚠️ LocalStack Docker container is NOT running."
    echo "   ➤ To start it: docker-compose up -d"
fi

# 2. Check if LocalStack CLI is available
if ! command -v localstack &> /dev/null; then
    echo "⚠️ LocalStack CLI not found in this environment."
    echo "   ➤ If it's in requirements.txt, ensure the virtual environment is active (it is ✅)."
    echo "   ➤ Or install manually: pip install localstack"
else
    echo "✅ LocalStack CLI is installed: $(localstack --version)"
fi

echo "-------------------------"
echo "� Bootstrap complete!"
echo ""
echo "You can now run:"
echo "  ▶ ./create_test_data.sh"
echo "  ▶ ./run_test_data.sh"
echo "  ▶ ./run-pytest-mac.sh"
echo "  ▶ ./check_pep8.sh"

