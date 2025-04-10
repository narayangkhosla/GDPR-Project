param (
    [string]$Region = "eu-west-2",
    [string]$FunctionName = "gdpr-obfuscator",
    [string]$Runtime = "python3.11",
    [string]$Handler = "main.lambda_handler",
    [string]$Role = "arn:aws:iam::000000000000:role/lambda-exec-role",
    [string]$LayerArn = "",  # Leave empty if not using a layer
    [string]$ZipFile = "gdpr_lambda.zip"
)

$awslocal = ".\.venv\Scripts\awslocal.bat"

Write-Host ""
Write-Host "=== Deploying Lambda: $FunctionName to region $Region ==="

# Function to check if LocalStack Lambda service is responsive
function Check-LocalStackLambda {
    Write-Host "`nChecking if LocalStack Lambda service is responsive..."
    $maxAttempts = 10
    $attempt = 0
    $ready = $false

    do {
        & "$awslocal" lambda list-functions --region $Region > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            $ready = $true
        } else {
            Start-Sleep -Seconds 2
            $attempt++
        }
    } while (-not $ready -and $attempt -lt $maxAttempts)

    if (-not $ready) {
        Write-Error "ERROR: LocalStack Lambda service is not responding. Is it running?"
        exit 1
    }

    Write-Host "LocalStack is ready."
}

# Function to clean and prepare build directory
function Prepare-BuildDirectory {
    Write-Host "Preparing build directory..."

    if (Test-Path "build") {
        Remove-Item -Recurse -Force "build"
    }
    New-Item -ItemType Directory -Path "build" | Out-Null
    Set-Location "build"
}

# Function to install deployment dependencies
function Install-Dependencies {
    Write-Host "Installing deployment dependencies..."
    pip install -r ../deployment-requirements.txt -t . | Out-Null
}

# Function to create the ZIP package
function Create-ZipPackage {
    Write-Host "Creating ZIP package..."
    Set-Location ..
    if (Test-Path $ZipFile) {
        Remove-Item $ZipFile
    }
    Compress-Archive -Path .\build\* -DestinationPath $ZipFile

    if (Test-Path $ZipFile) {
        $zipSizeMB = [math]::Round((Get-Item $ZipFile).Length / 1MB, 2)
        Write-Host "Created ZIP package: $ZipFile - $zipSizeMB MB"
    } else {
        Write-Error "ERROR: ZIP package was not created."
        exit 1
    }
}

# Function to delete existing Lambda function if it exists
function Delete-ExistingLambda {
    Write-Host "Checking for existing Lambda function: $FunctionName"
    $output = & "$awslocal" lambda get-function --function-name $FunctionName --region $Region 2>&1

    if ($output -match "Function not found") {
        Write-Host "No existing Lambda function found. Proceeding..."
    } else {
        Write-Host "Existing function found. Deleting..."
        & "$awslocal" lambda delete-function --function-name $FunctionName --region $Region | Out-Null
        Write-Host "Deleted existing Lambda function."
    }
}

# Function to create the Lambda function
function Create-LambdaFunction {
    Write-Host "Creating Lambda function '$FunctionName'..."
    
    $fullCommand = "$awslocal lambda create-function --function-name `"$FunctionName`" --runtime `"$Runtime`" --handler `"$Handler`" --role `"$Role`" --zip-file fileb://$ZipFile --region $Region"

    Write-Host "`nRunning command:"
    Write-Host $fullCommand
    Invoke-Expression $fullCommand

    # Check result
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Lambda function '$FunctionName' created successfully."
    } else {
        Write-Error "ERROR: Failed to create Lambda function. Check the above output for details."
        exit 1
    }
}

# Main deployment steps
Check-LocalStackLambda
Prepare-BuildDirectory
Install-Dependencies
Create-ZipPackage
Delete-ExistingLambda
Create-LambdaFunction
