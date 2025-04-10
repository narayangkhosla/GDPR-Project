param (
    [string]$FunctionName = "gdpr-obfuscator",
    [string]$Runtime = "python3.11",
    [string]$Handler = "main.lambda_handler",
    [string]$Role = "arn:aws:iam::000000000000:role/lambda-exec-role",
    [string]$ZipFile = "gdpr_lambda.zip",
    [string]$Region = "eu-west-2"
)

$awslocal = ".\.venv\Scripts\awslocal.bat"  # Initialize awslocal before use

Write-Host ""
Write-Host "=== Lambda Deployment Script ==="
Write-Host "Region: $Region"
Write-Host "Function Name: $FunctionName"
Write-Host "Handler: $Handler"
Write-Host "Runtime: $Runtime"
Write-Host "ZIP File: $ZipFile"

# Check and delete existing Lambda function if it exists
Write-Host "Checking for existing Lambda function '$FunctionName'..."
$output = & $awslocal lambda get-function --function-name $FunctionName --region $Region 2>&1

if ($output -match "Function not found") {
    Write-Host "No existing Lambda function found. Proceeding..."
} else {
    Write-Host "Function '$FunctionName' exists. Deleting..."
    & $awslocal lambda delete-function --function-name $FunctionName --region $Region | Out-Null
    Write-Host "Deleted existing Lambda function."
}

# Dynamically fetch the latest published layer ARN
$layerName = "pandas-layer"
$layerListJson = & $awslocal lambda list-layer-versions --layer-name $layerName --region $Region | ConvertFrom-Json

# Ensure layer ARN is fetched
if ($layerListJson.LayerVersions.Count -gt 0) {
    $LayerArn = $layerListJson.LayerVersions[0].LayerVersionArn
    Write-Host "Using Layer: $LayerArn"
} else {
    Write-Error "ERROR: Layer '$layerName' not found. Make sure the layer is published first."
    exit 1
}

# Construct the create-function command
Write-Host "`nCreating Lambda function '$FunctionName'..."

$fullCommand = "$awslocal lambda create-function --function-name `"$FunctionName`" --runtime `"$Runtime`" --handler `"$Handler`" --role `"$Role`" --zip-file fileb://$ZipFile --region $Region"

Write-Host "`nRunning command:"
Write-Host $fullCommand
Invoke-Expression $fullCommand

# Report result
if ($LASTEXITCODE -eq 0) {
    Write-Host "Lambda function '$FunctionName' created successfully."

    # ✅ Update configuration to attach layer AFTER creation
    if ($LayerArn -ne "") {
        Write-Host "Attaching layer via update-function-configuration..."

        $updateCommand = "$awslocal lambda update-function-configuration --function-name `"$FunctionName`" --layers $LayerArn --region $Region"

        Write-Host "Running command:"
        Write-Host $updateCommand
        $output = Invoke-Expression $updateCommand 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "Layer attached successfully."
            Write-Host $output
        } else {
            Write-Host "Failed to attach layer. Output:"
            Write-Host $output
        }
    }
} else {
    Write-Host "ERROR: Failed to create Lambda function. Check the above output for details."
}
