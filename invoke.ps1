param (
    [string]$FunctionName = "gdpr-obfuscator",
    [string]$PayloadFile = "event.json",
    [string]$OutputFile = "output.json",
    [string]$Region = "eu-west-2"  # ✅ Centralized region
)

# Path to awslocal inside virtual environment
$AwsLocal = ".\.venv\Scripts\awslocal.bat"

Write-Host "`nInvoking Lambda function '$FunctionName' with payload from '$PayloadFile' in region '$Region'..."

# Check if awslocal exists
if (!(Test-Path $AwsLocal)) {
    Write-Error "awslocal is not installed or not found at '$AwsLocal'."
    exit 1
}

# Check if payload file exists
if (!(Test-Path $PayloadFile)) {
    Write-Error "Payload file '$PayloadFile' not found."
    exit 1
}

# Validate payload is valid JSON
try {
    Get-Content $PayloadFile | ConvertFrom-Json | Out-Null
} catch {
    Write-Error "Invalid JSON in '$PayloadFile': $_"
    exit 1
}

# Invoke Lambda using awslocal
& $AwsLocal --region $Region lambda invoke `
    --function-name $FunctionName `
    --payload file://$PayloadFile `
    --cli-binary-format raw-in-base64-out `
    $OutputFile

Write-Host "`n✅ Response saved to '$OutputFile'"
