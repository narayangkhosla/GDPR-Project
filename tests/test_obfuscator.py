import pytest
import time
import logging
from src.obfuscator import obfuscate_csv


def test_obfuscate_csv():
    input_data = "student_id,name,email_address\n123,John Smith,john@example.com"
    pii_fields = ["name", "email_address"]
    output = obfuscate_csv(input_data, pii_fields).decode("utf-8")
    assert "***" in output
    assert "John Smith" not in output
    assert "john@example.com" not in output


#  Only specified fields are obfuscated
def test_obfuscate_specified_fields_only():
    input_data = "id,name,email,course\n1,John,john@example.com,CS"
    pii_fields = ["name", "email"]
    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")
    assert "***" in result
    assert "John" not in result
    assert "john@example.com" not in result
    assert "CS" in result  # Unaffected


# Field missing in header
def test_field_not_in_header():
    input_data = "id,name\n1,John"
    pii_fields = ["email"]
    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")
    assert "***" not in result  # No obfuscation


# Fields are case-sensitive
def test_field_case_sensitivity():
    input_data = "id,Name,Email\n1,John,john@example.com"
    pii_fields = ["name", "email"]  # Lowercase
    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")
    assert "John" in result
    assert "john@example.com" in result


# Field exists but value is empty
def test_field_value_is_empty():
    input_data = "id,name,email\n1,,john@example.com"
    pii_fields = ["name", "email"]
    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")
    assert ",***," in result


# Field exists but already obfuscated
def test_field_already_obfuscated():
    input_data = "id,name,email\n1,***,***"
    pii_fields = ["name", "email"]
    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")
    assert result.count("***") == 2  # No double obfuscation


# No matching fields to obfuscate
def test_no_fields_to_obfuscate():
    input_data = "id,name,email\n1,John,john@example.com"
    pii_fields = ["phone"]
    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")
    assert "John" in result
    assert "john@example.com" in result


# multiple rows
def test_multiple_rows():
    input_data = "id,name,email\n" "1,John,john@example.com\n" "2,Jane,jane@example.com"
    pii_fields = ["email"]
    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")
    assert result.count("***") == 2


# Ensure obfuscate_csv() returns a bytes object (for S3 PutObject compatibility).
def test_obfuscate_returns_bytes():
    input_data = "id,name,email\n1,John,john@example.com"
    pii_fields = ["email"]
    result = obfuscate_csv(input_data, pii_fields)
    assert isinstance(result, bytes)


# Ensure non-CSV formatted input raises a clean error or fails gracefully.
def test_obfuscate_non_csv_input():
    non_csv_data = '{"id": 1, "name": "John"}'
    pii_fields = ["name"]
    with pytest.raises(ValueError):
        obfuscate_csv(non_csv_data, pii_fields)


# Performance Test (File <1MB in <1min)
# Let’s simulate a large file (~5000+ rows) and ensure it processes under 1 second.
def test_obfuscation_under_1mb_and_1_minute():
    # Generate a large CSV string ~0.5–1MB
    header = "id,name,email\n"
    row = "1,John,john@example.com\n"
    csv_data = header + row * 50000  # ~1MB
    pii_fields = ["name", "email"]

    start = time.time()
    result = obfuscate_csv(csv_data, pii_fields)
    end = time.time()

    assert isinstance(result, bytes)
    assert end - start < 60  # under 1 minute


def test_no_pii_logged_during_obfuscation(caplog):
    input_data = "id,name,email\n1,John,john@example.com"
    pii_fields = ["name", "email"]

    with caplog.at_level(logging.INFO):
        obfuscate_csv(input_data, pii_fields)

    # Ensure no PII or row data was logged
    log_output = " ".join(caplog.messages)
    assert "John" not in log_output
    assert "john@example.com" not in log_output
    assert "1" not in log_output
    assert "email" not in log_output  # Optional: block even column names

    # But a safe log message *was* made
    assert "Starting obfuscation" in log_output


# File with Only Headers, No Rows
def test_csv_with_only_headers():
    input_data = "id,name,email\n"
    pii_fields = ["name", "email"]
    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")

    # Should return only the header row, unchanged
    assert result.strip() == "id,name,email"


# CSV with Missing Values / Malformed Rows
def test_csv_with_missing_values():
    input_data = "id,name,email\n1,,john@example.com\n2,Jane,\n3,,"
    pii_fields = ["name", "email"]
    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")

    # 3 rows × 2 PII fields = 6 obfuscated values (even empty ones)
    assert result.count("***") == 6


# pii_fields Containing a Non-String (e.g., None, 123)
def test_pii_fields_with_non_string_entries():
    input_data = "id,name,email\n1,John,john@example.com"
    pii_fields = ["name", None, 123]

    with pytest.raises(TypeError):
        obfuscate_csv(input_data, pii_fields)


# PII Field Names with Leading/Trailing Spaces
def test_pii_fields_with_spaces():
    input_data = "id,name,email\n1,John,john@example.com"
    pii_fields = [" name ", " email "]

    result = obfuscate_csv(input_data, [f.strip() for f in pii_fields]).decode("utf-8")
    assert "***" in result
    assert "John" not in result
    assert "john@example.com" not in result


# CSV with Quoted Headers (e.g., "email_address")
def test_csv_with_quoted_headers():
    input_data = '"id","name","email"\n1,John,john@example.com'
    pii_fields = ["name", "email"]

    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")

    assert "***" in result
    assert "John" not in result
    assert "john@example.com" not in result
