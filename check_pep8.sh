#!/bin/bash

# Exit immediately if any command fails
set -e

# Define excluded folders/files (used by Ruff and Flake8)
excluded=".venv,__pycache__,build,dist,*.egg-info,lambda_layer"

echo "-----------------"
echo "Running Ruff for auto-fixable linting issues..."
ruff check . --fix --unsafe-fixes --exclude "$excluded"

echo "-----------------"
echo "Formatting code with Black..."
black . --exclude '/(\.venv|__pycache__|build|dist|lambda_layer|.*\.egg-info)/'

echo "-----------------"
echo "Running Flake8 for style checks..."
flake8 . --exclude="$excluded"

echo "-----------------"
echo "✅ All checks are completed."
