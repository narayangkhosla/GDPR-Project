# This PowerShell script runs the GDPR Obfuscator for CSV, JSON, and Parquet using reusable logic.

# Set AWS environment variables for LocalStack
$env:AWS_ACCESS_KEY_ID = "test"
$env:AWS_SECRET_ACCESS_KEY = "test"
$env:AWS_DEFAULT_REGION = "eu-west-2"
$env:AWS_ENDPOINT_URL = "http://localhost:4566"

# Define a reusable function BEFORE use
function Invoke-Obfuscation {
    param (
        [string]$format,
        [string]$bucket,
        [string]$resultsPath,
        [string]$outputPrefix,
        [string[]]$fields
    )

    $inputFile = "sample.$format"
    $outputFile = "$resultsPath/$outputPrefix.$format"

    Write-Host "`n=== Running CLI for $format ==="

    python .\src\main.py --s3 "s3://$bucket/$inputFile" --fields $fields --output $outputFile

    if ($LASTEXITCODE -eq 0 -and (Test-Path $outputFile)) {
        Write-Host "$format written to $outputFile"
    }
    else {
        Write-Host "❌ Failed to obfuscate $format"
    }
}

# Initial setup
$bucket = "test-bucket"
$outputPrefix = "obfuscated_sample_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$extensions = @("csv", "json", "parquet")
$resultsPath = "./results"
$fields = @("name1", "email_address")

# Ensure results directory exists and is empty
if (Test-Path $resultsPath) {
    Remove-Item "$resultsPath/*" -Force
}
else {
    New-Item -ItemType Directory -Path $resultsPath | Out-Null
}

Write-Host "`nChecking if bucket '$bucket' exists..."
$bucketExists = awslocal s3 ls | Select-String $bucket

if ($bucketExists) {
    Write-Host "`nBucket '$bucket' already exists."
    $choice = Read-Host "Would you like to continue with this bucket? (Y/N)"
    if ($choice -ne "Y" -and $choice -ne "y") {
        $bucket = Read-Host "Enter a new bucket name"
        Write-Host "Creating new bucket '$bucket'..."
        awslocal s3 mb "s3://$bucket"
    }
    else {
        Write-Host "Continuing with existing bucket '$bucket'."
    }
}
else {
    Write-Host "Creating bucket '$bucket'..."
    awslocal s3 mb "s3://$bucket"
}

Write-Host "`nUploading test files to bucket '$bucket'..."
awslocal s3 cp sample.csv "s3://$bucket/sample.csv"
awslocal s3 cp sample.json "s3://$bucket/sample.json"
awslocal s3 cp sample.parquet "s3://$bucket/sample.parquet"

# Run obfuscation per format
Invoke-Obfuscation -format "csv" -bucket $bucket -resultsPath $resultsPath -outputPrefix $outputPrefix -fields $fields
Invoke-Obfuscation -format "json" -bucket $bucket -resultsPath $resultsPath -outputPrefix $outputPrefix -fields $fields
Invoke-Obfuscation -format "parquet" -bucket $bucket -resultsPath $resultsPath -outputPrefix $outputPrefix -fields $fields

# Summary
Write-Host "`n========= SUMMARY =========="
foreach ($ext in $extensions) {
    $outputFile = "$resultsPath/$outputPrefix.$ext"
    if (Test-Path $outputFile) {
        Write-Host "==> SUCCESS :: The obfuscated $ext data has been written to $outputFile"
    }
    else {
        Write-Host ":XX WARNING :: No $ext output file was written (possible error during obfuscation)"
    }
}

Write-Host "`nNOTE: If no fields were obfuscated, it's likely that the specified field names did not match the data headers."
Write-Host "Please double-check the field names passed to '--fields' in the CLI."
