# 🛡️ GDPR Obfuscator Tool

## Introduction

A Python-based utility to anonymize personally identifiable information (PII) from structured data files stored in Amazon S3.  
It replaces specified sensitive fields with obfuscated values (e.g., `"***"`) in compliance with GDPR.

Supports:

- ✅ CSV
- ✅ JSON
- ✅ Parquet

## Tech Stack

- **Programming Language**: Python 3.13.2
- **Core Libraries**: Pandas, Numpy, Boto3, PyArrow
- **Testing Framework:** Pytest
- **AWS Services (via LocalStack):** S3, Lambda
- **Code Quality & Security Tools:**
  - Ruff (linting and auto-fixing)
  - Flake8 (style checks)
  - Black (code formatter)
  - Bandit (security scanning)
- **Environment Management:** `venv` (Python built-in)
- **Shell Scripts:** Bash (`.sh`) and PowerShell (`.ps1`)
- **Version Control:** Git + GitHub

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

project-root/ │ ├── src/ # All source code │ ├── main.py # CLI + core handler (MVP entry point) │ ├── obfuscator.py # Logic for obfuscating CSV, JSON, Parquet │ ├── s3_utils.py # Handles S3 fetch/upload │ ├── exceptions.py # Custom error handling │ └── logging_utils.py # Configures file + console loggers │ ├── tests/ # Pytest test suite (no Lambda, pure handler-based) │ ├── create_test_data.ps1 # Generates randomized sample.csv, .json, .parquet ├── run_test_data.ps1 # End-to-end local test runner using LocalStack ├── read_parq_file.py # Reads and prints obfuscated Parquet output ├── requirements.txt # Python dependencies └── .gitattributes # Line ending consistency across OSs

---

## 🎯 MVP Objectives

| Requirement                                                         | Met                               |
| ------------------------------------------------------------------- | --------------------------------- |
| Accept JSON input with S3 URI + PII fields                          | ✅                                |
| Process CSV files                                                   | ✅                                |
| Obfuscate specified fields                                          | ✅                                |
| Return obfuscated output as bytes (suitable for `boto3.put_object`) | ✅                                |
| Testable without AWS                                                | ✅ (uses LocalStack)              |
| CLI support                                                         | ✅                                |
| Lambda handler                                                      | ❌ (deliberately excluded in MVP) |

---

## 🚀 How to Run the Program

### <u>If you are on a WINDOWS machine, perform the following steps:</u>

The project provides two PowerShell scripts to help you test the obfuscation workflow from start to finish using local data and LocalStack S3.

#### Step 1. 📦 Create and activate your virtual environment:

    python -m venv .venv
    .venv\Scripts\Activate.ps1

#### Step 2. 📦 Generate Sample Test Data:

Run this script to create test files containing sample Personal Identifiable Information (PII):

    .\create_test_data.ps1

This will generate the below files (at the project/root level):

- sample.csv
- sample.json
- sample.parquet

#### Step 3. 🧪 **Run the Obfuscation Workflow**:

Run this script to:

- Upload the sample files to your LocalStack S3 bucket
- Obfuscate the selected PII fields
- Save the results to local output file(s)

        .\run_test_data.ps1

### <u>If you are on a MAC machine, perform the following steps:</u>

#### Step 1. 📦 Create and activate your virtual environment:

    python -m venv .venv
    source .venv/bin/activate

#### Step 2. 📦 Run the following script:

    bash ./bootstrap_project.sh

This purpose of this file is to:

- Install all dependencies
- Make helper scripts (i.e., create_test_data.sh, run_test_data.sh, check_pep8.sh, run-pytest-mac.sh) executable
- Verify that LocalStack is running

### ⚙️ Working of .\run_test_data.ps1 (Windows)

### OR

### bash ./run_test_data.sh (Mac)

📝 Field Specification
You can specify the fields to obfuscate using a comma-separated string(s):

    $fields = @("name", "email_address") - for Windows

    fields="name email_address" - for Mac

These fields are passed to the CLI using the --fields argument.

✅ Smart Obfuscation Logic
The script uses intelligent logic to ensure only meaningful files are written:

- ✅ **If all specified fields match:**
  All matching fields are obfuscated, and a success message is shown, for example:

        Obfuscated file written to ./results/obfuscated_sample_20250502_155814.csv

- ⚠️ **If some fields match, and some don’t:**
  Only the valid fields are obfuscated, and a warning is printed listing the non-matching fields. For example, if I had passed name1 (instead of name), email_address, it will obfuscate email_address, and leave rest as is.

        ⚠️Some PII fields were not found in JSON: name1

        Obfuscated file written to ./results/obfuscated_sample_20250502_161335.csv

- ❌ **If none of the fields match:**
  The obfuscator skips writing the output file, and prints a clear error message in the terminal, for example:

          ⚠️ None of the specified PII fields were found in the CSV file.

          ❌ Error: No matching PII fields found — obfuscation skipped.

  By default, All obfuscated files are saved in a dedicated `results/` folder:

- `results/obfuscated_sample_YYYYMMDD_HHMMSS.csv`
- `results/obfuscated_sample_YYYYMMDD_HHMMSS.json`
- `results/obfuscated_sample_YYYYMMDD_HHMMSS.parquet`

Example:
obfuscated_sample_20250430_193557.csv

You’ll also see confirmation messages like:
`"The obfuscated csv data has been written to resuts/obfuscated_sample_20250430_193557.csv"`

### 🔍 <u>Checking the Output</u>

Check the `results/` folder.

- For both **CSV** and **JSON** files, you can simply open them directly to view the obfuscated data.
- For **Parquet** files, use the following command to preview the obfuscated output:

  ```bash
  python read_parq_file.py
  ```

  This will automatically detect and read the **most recently generated** Parquet file from the `results/` folder.

  💡 To view a specific file, use the `--file` argument (just the filename, no path needed):

  ```bash
  python read_parq_file.py --file obfuscated_sample_20250501_132159.parquet
  ```

## ✅ Running Tests with Pytest

All unit and functional tests are written using Pytest and located in the tests/ folder.

### <u>On a WINDOWS machine:</u>

To run the relevant tests (excluding Lambda-related files), use

a. this command if you are in the `tests\` folder:

    pytest -v @(Get-ChildItem -Recurse -Filter "test_*.py" | Where-Object {
        $_.Name -notin @("test_integration.py", "test_lambda_end_to_end.py")
    } | ForEach-Object { $_.FullName })

b. this command if you are in the `project\` folder:

    pytest -v @(Get-ChildItem -Recurse -Path "tests" -Filter "test_*.py" | Where-Object {
    $_.Name -notin @("test_integration.py", "test_lambda_end_to_end.py")
    } | ForEach-Object { $_.FullName })

### <u>On a MAC machine, Run:</u>

a. this command if you are in the `tests\` folder:

    bash ../run-pytest-mac.sh

b. this command if you are in the `project\` folder:

    bash ./run-pytest-mac.sh

Both of the above commands will:

- ✅ Run all test files matching test\_\*.py
- ❌ Exclude test_integration.py and test_lambda_end_to_end.py, which are related to Lambda-based functionality that is not part of the MVP.

## 🐳 Using LocalStack with Docker

This project relies on [LocalStack](https://docs.localstack.cloud/) to emulate AWS S3 services locally for testing.

To use LocalStack, you must have **Docker** installed on your system.

### ✅ Install Docker

- macOS: [Install Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
- Windows: [Install Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)

### ✅ Start LocalStack

If LocalStack is installed globally (via `brew`, `pip`, or system package manager):

```bash
localstack start

## ⚙️ Setup

### ✅ 1. Install Requirements

    pip install -r requirements.txt

### 🚀 2. Run LocalStack

This tool is tested using LocalStack.

    localstack start

### 🧪 3. Generate Test Data

Refer to the above mentioned steps, depending on the Operating System.

### 🛠️ 4. Run End-to-End Obfuscation Tests

Refer to the above mentioned steps, depending on the Operating System.

### 🔍 5. Inspect Parquet Output (Optional)

    python read_parq_file.py

### 💻 CLI Usage

    python main.py --s3 s3://test-bucket/sample.csv --fields name email_address

    Optional flags:
    --output <filename> – save obfuscated result to file
    --encoding <utf-8|utf-16|latin-1> – force specific file encoding

### 🧪 Test Coverage

This project includes comprehensive test coverage across all core components using `pytest`.
Each test is grouped by the module it targets (e.g., CSV obfuscation, S3 utilities, input validation).
Tests verify functionality, error handling, edge cases, and integration across supported file formats (CSV, JSON, Parquet).

Below is a categorized list of all test cases:

### 📁 test_bandit_scan.py
- test_bandit_scan
- test_bandit_scan

### 📁 test_exceptions.py
- test_s3_object_not_found_error_message
- test_s3_object_not_found_error_raises

### 📁 test_input_validation.py
- test_empty_file_path
- test_empty_pii_fields_list
- test_file_extension_unsupported_type
- test_invalid_json_input
- test_malformed_s3_uri
- test_missing_file_key
- test_missing_pii_fields_key
- test_pii_fields_not_a_list

### 📁 test_obfuscate_handler_formats.py
- test_csv_file_obfuscates_successfully
- test_json_file_obfuscates_successfully
- test_lambda_json_file_obfuscates_successfully
- test_lambda_parquet_file_obfuscates_successfully
- test_parquet_file_obfuscates_successfully

### 📁 test_obfuscator.py
- test_csv_with_missing_values
- test_csv_with_only_headers
- test_csv_with_quoted_headers
- test_field_already_obfuscated
- test_field_case_sensitivity
- test_field_not_in_header
- test_field_value_is_empty
- test_json_field_case_insensitivity
- test_multiple_rows
- test_no_fields_to_obfuscate
- test_no_pii_logged_during_obfuscation
- test_obfuscate_csv
- test_obfuscate_handler_json
- test_obfuscate_handler_parquet
- test_obfuscate_json_invalid_json
- test_obfuscate_json_invalid_structure
- test_obfuscate_json_list_of_objects
- test_obfuscate_json_missing_fields
- test_obfuscate_json_single_object
- test_obfuscate_non_csv_input
- test_obfuscate_parquet_invalid_format
- test_obfuscate_parquet_valid
- test_obfuscate_returns_bytes
- test_obfuscate_specified_fields_only
- test_obfuscation_under_1mb_and_1_minute
- test_parquet_field_case_insensitivity
- test_pii_fields_with_non_string_entries
- test_pii_fields_with_spaces

### 📁 test_s3_utils.py
- test_fetch_file_from_s3
- test_fetch_file_from_s3
- test_fetch_file_from_s3
- test_fetch_file_from_s3_file_not_found
- test_fetch_file_with_encoding_override
- test_logs_encoding_detected

### ⚠️ Known Exclusions (by design)

| Feature                              | Included? | Notes                                       |
| ------------------------------------ | --------- | ------------------------------------------- |
| Lambda handler                       | ❌        | Can be added later                          |
| Step Functions, EventBridge, Airflow | ❌        | Invocation logic out of MVP scope           |
| IAM, AWS credentials                 | ❌        | Uses dummy test credentials via LocalStack  |
| Output S3 write logic in handler     | ❌        | Done by caller, not the handler (by design) |

### 🧰 Design Principles

- **Input**: JSON with file_to_obfuscate and pii_fields
- **Output**: Byte stream with obfuscated fields
- **File Types**: .csv, .json, .parquet
- **Field Redaction**: "\*\*\*" for specified fields
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
```
