# 🛡️ GDPR Obfuscator Tool

## Introduction
A Python-based utility to anonymize personally identifiable information (PII) from structured data files stored in Amazon S3.  
It replaces specified sensitive fields with obfuscated values (e.g., `"***"`) in compliance with GDPR.

Supports:
- ✅ CSV
- ✅ JSON
- ✅ Parquet

## Tech Stack
- Programming Language: Python
- Libraries: Pandas, Numpy, Boto3, Pytest, PyArrow 

## ✨ Features
- **Obfuscation of PII fields**: Replaces sensitive values (e.g., name, email) with `***` to comply with GDPR standards.
- **Multi-format file support**: Handles CSV, JSON, and Parquet files stored in S3 buckets.
- **S3-based data ingestion**: Accepts S3 URI and field list via structured JSON input.
- **Output as byte stream**: Generates obfuscated files compatible with boto3.put_object for immediate re-upload to S3.
- **MVP-focused modular design**: Separates obfuscation logic from storage/output logic — ideal for integration into larger pipelines.
- **Simple CLI interface**: Offers command-line support for local testing and demo purposes.
- **Testable with LocalStack**: No AWS account required; uses dummy credentials and LocalStack to emulate S3 operations.
- **Extensible architecture**: Initially built for CSV, extended to support JSON and Parquet.
- **Compliant with coding standards**: Written in Python, unit-tested, PEP8-compliant, and designed for security and deployability.
- **Deployment-ready design**: Although Lambda is not used in the MVP, the tool’s structure allows seamless integration into AWS Lambda, Step Functions, or Airflow workflows in future phases.

## 📁 Project Structure

project-root/ │ ├── src/ # All source code │ ├── main.py # CLI + core handler (MVP entry point) │ ├── obfuscator.py # Logic for obfuscating CSV, JSON, Parquet │ ├── s3_utils.py # Handles S3 fetch/upload │ ├── exceptions.py # Custom error handling │ └── logging_utils.py # Configures file + console loggers │ ├── tests/ # Pytest test suite (no Lambda, pure handler-based) │ ├── create_test_data.ps1 # Generates randomized sample.csv, .json, .parquet ├── run_tests.ps1 # End-to-end local test runner using LocalStack ├── read_parq_file.py # Reads and prints obfuscated Parquet output ├── requirements.txt # Python dependencies └── .gitattributes # Line ending consistency across OSs


---

## 🎯 MVP Objectives

| Requirement | Met |
|-------------|-----|
| Accept JSON input with S3 URI + PII fields | ✅ |
| Process CSV files | ✅ |
| Obfuscate specified fields | ✅ |
| Return obfuscated output as bytes (suitable for `boto3.put_object`) | ✅ |
| Testable without AWS | ✅ (uses LocalStack) |
| CLI support | ✅ |
| Lambda handler | ❌ (deliberately excluded in MVP) |

---
## 🚀 How to Run the Program
The project provides two PowerShell scripts to help you test the obfuscation workflow from start to finish using local data and LocalStack S3.
#### 1. 📦 Generate Sample Test Data: 
Run this script to create test files containing sample Personal Identifiable Information (PII):

    .\create_test_data.ps1

This will generate the below files (at the project/root level):
- sample.csv
- sample.json
- sample.parquet

#### 2. 🧪 **Run the Obfuscation Workflow**: 
Run this script to:
- Upload the sample files to your LocalStack S3 bucket
- Obfuscate the selected PII fields
- Save the results to local output file

        .\run_test_data.ps1

By default, the output files will be named using a timestamp for easy versioning:

- `obfuscated_sample_YYYYMMDD_HHMMSS.csv`
- `obfuscated_sample_YYYYMMDD_HHMMSS.json`
- `obfuscated_sample_YYYYMMDD_HHMMSS.parquet`

Example:
obfuscated_sample_20250430_193557.csv

You’ll also see confirmation messages like:
`"The obfuscated csv data has been written to obfuscated_sample_20250430_193557.csv"`

## ✅ Running Tests with Pytest
All unit and functional tests are written using Pytest and located in the tests/ folder.

To run the relevant tests (excluding Lambda-related files), use 

a. this command if you are in the `tests\` folder:

    pytest -v @(Get-ChildItem -Recurse -Filter "test_*.py" | Where-Object {
        $_.Name -notin @("test_integration.py", "test_lambda_end_to_end.py")
    } | ForEach-Object { $_.FullName })

b. this command if you are in the `project\` folder:

    pytest -v @(Get-ChildItem -Recurse -Path "tests" -Filter "test_*.py" | Where-Object {
    $_.Name -notin @("test_integration.py", "test_lambda_end_to_end.py")
    } | ForEach-Object { $_.FullName })    

Both of the above commands will:
- ✅ Run all test files matching test_*.py
- ❌ Exclude test_integration.py and test_lambda_end_to_end.py, which are related to Lambda-based functionality that is not part of the MVP.

## ⚙️ Setup

### ✅ 1. Install Requirements

    pip install -r requirements.txt


### 🚀 2. Run LocalStack
  This tool is tested using LocalStack.

    localstack start

### 🧪 3. Generate Test Data
  Creates randomized data in:
- sample.csv
- sample.json
- sample.parquet
    
        .\create_test_data.ps1

### 🛠️ 4. Run End-to-End Obfuscation Tests
Uploads test files to S3, invokes CLI, and writes results:

    .\run_tests.ps1

Output includes:
- Obfuscated console output (for CSV & JSON)
- obfuscated_sample.parquet (for Parquet)

### 🔍 5. Inspect Parquet Output (Optional)
    python read_parq_file.py obfuscated_sample.parquet

### 💻 CLI Usage
    python main.py --s3 s3://test-bucket/sample.csv --fields name email_address

    Optional flags:
    --output <filename> – save obfuscated result to file
    --encoding <utf-8|utf-16|latin-1> – force specific file encoding

### 🧪 Testing
Tests are written in tests/ using pytest, focused on obfuscate_handler() (not Lambda).
    pytest -v

Sample tests:
- Obfuscate CSV, JSON, and Parquet from S3
- Validate field redaction

### ⚠️ Known Exclusions (by design)

| Feature | Included? | Notes |
|---------|-----------|-------|
| Lambda handler | ❌ | Can be added later |
| Step Functions, EventBridge, Airflow | ❌ | Invocation logic out of MVP scope |
| IAM, AWS credentials | ❌ | Uses dummy test credentials via LocalStack |
| Output S3 write logic in handler | ❌ | Done by caller, not the handler (by design) |

### 🧰 Design Principles
- **Input**: JSON with file_to_obfuscate and pii_fields
- **Output**: Byte stream with obfuscated fields
- **File Types**: .csv, .json, .parquet
- **Field Redaction**: "***" for specified fields
- **Encoding**: Auto-detected or override via --encoding
- **Error Handling**: Custom exceptions for unsupported formats, bad URIs, missing files

### 📝 License
This project is provided for internal and educational use. Licensing terms can be defined as needed.

### 🙋 Support & Contributions
Have ideas, bugs, or suggestions? Open a GitHub issue or start a discussion!

## 🧹 Files Not Relevant to MVP

During initial development, several deployment and Lambda-related files were created. However, these are **not required** to meet the MVP and can be ignored for the purpose of technical review.

The following files are safe to skip:

- `create-f.ps1`, `deploy_new.ps1`, `invoke.ps1`
- `create-layer.ps1`, `publish-layer.bat`
- `event.json`, `output.json`
- `deployment-requirements.txt`
- `pytest.ini`

These were part of an **early prototype** for AWS Lambda integration and are included here for reference only.  
👉 The project meets the MVP using the CLI, LocalStack, and handler-based testing with no Lambda code required.
