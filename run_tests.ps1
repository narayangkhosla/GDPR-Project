# This powershell file does the following:
# Sets environment variables
# Checks if the bucket exists
# Prompts the user whether to continue or enter a new bucket
# Uploads the CSV, JSON, and Parquet files
# Runs your main.py CLI for all formats

# Set environment variables for AWS/LocalStack
$env:AWS_ACCESS_KEY_ID = "test"
$env:AWS_SECRET_ACCESS_KEY = "test"
$env:AWS_DEFAULT_REGION = "eu-west-2"
$env:AWS_ENDPOINT_URL = "http://localhost:4566"

# Default bucket name
$bucket = "test-bucket"

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

Write-Host "`n=== Running CLI for CSV ==="
python .\src\main.py --s3 "s3://$bucket/sample.csv" --fields name email_address --output obfuscated_sample.csv

Write-Host "`n=== Running CLI for JSON ==="
python .\src\main.py --s3 "s3://$bucket/sample.json" --fields name email_address --output obfuscated_sample.json

Write-Host "`n=== Running CLI for Parquet ==="
python .\src\main.py --s3 "s3://$bucket/sample.parquet" --fields name email_address --output obfuscated_sample.parquet

Write-Host "`n=== DONE ==="
Read-Host "Press ENTER to exit"
