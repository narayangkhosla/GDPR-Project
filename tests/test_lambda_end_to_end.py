import json
from unittest.mock import patch
import pytest
from main import lambda_handler
from s3_utils import get_s3_client


# I am using parameterization features and moto fixtures
# to simulate realistic S3 setups — including alternate buckets,
# field variations, and UTF-16/JSON formats.
@pytest.mark.parametrize(
    "input_key", ["sample.csv", "uploads/data.csv", "nested/path/file.csv"]
)
def test_lambda_with_varied_filenames(s3_bucket, input_key):
    s3 = get_s3_client()
    output_key = f"obfuscated/{input_key.split('/')[-1]}"
    csv_content = "id,name,email\n1,Alice,alice@example.com"

    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=csv_content)

    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ]
    }

    response = lambda_handler(event, context=None)
    obfuscated = s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode()

    assert "***" in obfuscated
    assert "Alice" not in obfuscated
    assert response["statusCode"] == 200


@pytest.mark.parametrize(
    "pii_fields,csv_content,expected_stars",
    [
        (["name"], "id,name,email\n1,Anna,anna@example.com", 1),
        (["email"], "id,name,email\n1,Anna,anna@example.com", 1),
        (["name", "email"], "id,name,email\n1,Anna,anna@example.com", 2),
    ],
)
def test_lambda_with_varied_fields(s3_bucket, pii_fields, csv_content, expected_stars):
    s3 = get_s3_client()
    input_key = "test.csv"
    output_key = "obfuscated/test.csv"

    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=csv_content)

    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ]
    }

    from obfuscator import obfuscate_csv

    result = obfuscate_csv(csv_content, pii_fields)

    # ✅ Patch where obfuscate_handler is used (main.py)
    with patch("main.obfuscate_handler") as mock_handler:
        mock_handler.return_value = result
        lambda_handler(event, context=None)

    obfuscated = s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode()
    assert obfuscated.count("***") == expected_stars


def test_lambda_utf16_encoded_file(s3_bucket):
    s3 = get_s3_client()
    input_key = "utf16.csv"
    output_key = "obfuscated/utf16.csv"
    csv_content = "id,name,email\n1,Bob,bob@example.com".encode("utf-16")

    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=csv_content)

    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ]
    }

    lambda_handler(event, context=None)
    result = (
        s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode("utf-8")
    )

    assert "***" in result
    assert "Bob" not in result


# JSON File (Should fail gracefully if unsupported)
def test_lambda_json_file_obfuscates_successfully(s3_bucket):
    s3 = get_s3_client()
    input_key = "data.json"
    output_key = "obfuscated/data.json"
    data = [{"id": 1, "name": "Eve", "email": "eve@example.com"}]

    s3.put_object(
        Bucket=s3_bucket, Key=input_key, Body=json.dumps(data).encode("utf-8")
    )

    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ]
    }

    response = lambda_handler(event, context=None)
    result = (
        s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode("utf-8")
    )

    assert "***" in result
    assert "Eve" not in result
    assert response["statusCode"] == 200


# This following test will:
# Upload an obfuscated file before the Lambda runs
# Then trigger the Lambda
# Assert that the Lambda skips writing, and returns 409 Conflict


def test_lambda_skips_if_output_file_exists(s3_bucket, monkeypatch):
    monkeypatch.setenv("ENV", "prod")  # Override global "dev" default
    s3 = get_s3_client()
    input_key = "sample.csv"
    output_key = "obfuscated/sample.csv"  # Must match Lambda's output_key
    content = "id,name,email\n1,Eve,eve@example.com"

    # Upload the input file
    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=content)

    # Simulate that the output file already exists
    s3.put_object(Bucket=s3_bucket, Key=output_key, Body="existing content")

    # Simulate the S3 trigger event
    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ]
    }

    response = lambda_handler(event, context=None)

    assert response["statusCode"] == 409
    assert "already exists" in response["body"]

    # Confirm that the file was NOT overwritten
    existing = s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode()
    assert "existing content" in existing


# force=True - put_object() will run in this case
def test_lambda_force_overwrites_existing_file(s3_bucket):
    s3 = get_s3_client()
    input_key = "sample.csv"
    output_key = "obfuscated/sample.csv"
    original = "original content"
    updated = "id,name,email\n1,Overwrite,overwrite@example.com"

    # Upload input and simulated existing output
    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=updated)
    s3.put_object(Bucket=s3_bucket, Key=output_key, Body=original)

    # Lambda event with --force enabled
    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ],
        "force": True,
    }

    response = lambda_handler(event, context=None)

    # Assert it overwrote the file
    assert response["statusCode"] == 200
    result = s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode()
    assert "***" in result
    assert "Overwrite" not in result  # confirm PII was masked


# the following test will:
# Pre-create an obfuscated output file in S3
# Set the FORCE_OVERWRITE env var to "true"
# Run lambda_handler() without force in the event
# Verify that:
# The file was overwritten
# The status code is 200
# Obfuscation happened as expected


def test_lambda_env_force_overwrites_existing_file(s3_bucket, monkeypatch):
    s3 = get_s3_client()
    input_key = "sample.csv"
    output_key = "obfuscated/sample.csv"
    original = "original content"
    updated = "id,name,email\n1,Eve,eve@example.com"

    # Upload input file and an existing obfuscated output
    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=updated)
    s3.put_object(Bucket=s3_bucket, Key=output_key, Body=original)

    # Set environment variable FOR FORCE_OVERWRITE = true
    monkeypatch.setenv("FORCE_OVERWRITE", "true")

    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ]
        # ⚠️ No "force" key here
    }

    response = lambda_handler(event, context=None)

    # Verify overwrite succeeded
    assert response["statusCode"] == 200
    result = s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode()
    assert "***" in result
    assert "Eve" not in result


def test_lambda_env_dev_defaults_to_force(monkeypatch, s3_bucket):
    s3 = get_s3_client()
    input_key = "sample.csv"
    output_key = "obfuscated/sample.csv"
    original = "original content"
    updated = "id,name,email\n1,Test,test@example.com"

    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=updated)
    s3.put_object(Bucket=s3_bucket, Key=output_key, Body=original)

    monkeypatch.setenv("ENV", "dev")  # 🟢 Simulate dev mode

    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ]
    }

    response = lambda_handler(event, context=None)

    result = s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode()
    assert response["statusCode"] == 200
    assert "***" in result
    assert "Test" not in result
