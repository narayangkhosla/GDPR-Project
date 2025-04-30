# check_pep8.ps1

$excluded = ".venv,__pycache__,build,dist,*.egg-info,lambda_layer"

Write-Host "-----------------"
Write-Host "Running Ruff for auto-fixable linting issues..."
ruff check . --fix --unsafe-fixes --exclude $excluded

Write-Host "-----------------"
Write-Host "Formatting code with Black..."
black . --exclude "/(\.venv|__pycache__|build|dist|lambda_layer|.*\.egg-info)/"

Write-Host "-----------------"
Write-Host "Running Flake8 for style checks..."
flake8 . --exclude="$excluded"

# Write-Host "-----------------"
# Write-Host "Running Bandit for security analysis..."
# bandit -r . -x="$excluded"


Write-Host "-----------------"
Write-Host "All checks are completed."