param (
    [string]$Region = "eu-west-2",
    [string]$LayerName = "pandas-layer"
)

Write-Host "Creating Lambda layer '$LayerName' in region '$Region'..."

# Define paths
$layerPath = "lambda_layer"
$layerZip = "$LayerName.zip"
$awslocal = ".\.venv\Scripts\awslocal.bat"

# Validate awslocal CLI presence
if (!(Test-Path $awslocal)) {
    Write-Error "'awslocal.bat' not found at $awslocal. Make sure awscli-local is installed in your virtual environment."
    exit 1
}

# Clean previous build
if (Test-Path $layerPath) {
    Write-Host "Cleaning previous layer build..."
    Remove-Item -Recurse -Force $layerPath
}
New-Item -ItemType Directory -Path "$layerPath\python" | Out-Null

# Install packages
Write-Host "Installing pandas and pyarrow into the layer..."
pip install pandas pyarrow -t "$layerPath\python" | Out-Null

# ZIP the layer
if (Test-Path $layerZip) {
    Remove-Item $layerZip
}
Compress-Archive -Path "$layerPath\*" -DestinationPath $layerZip
Write-Host "Created ZIP layer package: $layerZip"

# Publish the layer to LocalStack
Write-Host "Publishing layer to LocalStack..."
& $awslocal --region $Region lambda publish-layer-version `
    --layer-name $LayerName `
    --zip-file fileb://$layerZip `
    --compatible-runtimes python3.11

Write-Host "Lambda layer '$LayerName' published successfully to LocalStack (region: $Region)"
