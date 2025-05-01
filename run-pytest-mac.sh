#!/bin/bash

# Move to the directory where this script is located (project root)
cd "$(dirname "$0")" || {
    echo "❌ Failed to navigate to script directory."
    exit 1
}

# Check for key project files to validate location
if [[ ! -d "tests" ]] || { [[ ! -f "pyproject.toml" ]] && [[ ! -f "requirements.txt" ]]; }; then
    echo "❌ This doesn't look like the project root. Missing tests/ or requirements."
    exit 1
fi

# Find test files (excluding specific ones)
mapfile -t test_files < <(find tests -type f -name "test_*.py" \
    ! -name "test_integration.py" \
    ! -name "test_lambda_end_to_end.py" 2>/dev/null)

# Handle no matches
if [[ ${#test_files[@]} -eq 0 ]]; then
    echo "❌ No matching test files found."
    exit 1
fi

# Run pytest
echo "✅ Running ${#test_files[@]} test(s)..."
pytest -v "${test_files[@]}"
