import json
import pytest
import time
import logging
import pandas as pd
import io
from obfuscator import obfuscate_csv, obfuscate_json, obfuscate_parquet


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
    with pytest.raises(ValueError, match="No matching PII fields"):
        obfuscate_csv(input_data, pii_fields)


# Fields are case-sensitive
def test_field_case_sensitivity():
    input_data = "id,Name,Email\n1,John,john@example.com"
    pii_fields = [
        "name",
        "email",
    ]  # Lowercase PII fields, should match regardless of header case
    result = obfuscate_csv(input_data, pii_fields).decode("utf-8")
    assert "***" in result
    assert "John" not in result
    assert "john@example.com" not in result


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
    pii_fields = ["phone"]  # no-match
    with pytest.raises(ValueError, match="No matching PII fields"):
        obfuscate_csv(input_data, pii_fields)


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


# Valid JSON list of objects
def test_obfuscate_json_list_of_objects():
    input_data = json.dumps(
        [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]
    )
    pii_fields = ["name", "email"]
    result = obfuscate_json(input_data, pii_fields).decode("utf-8")

    assert result.count("***") == 4
    assert "Alice" not in result
    assert "bob@example.com" not in result


# 	Valid single JSON object
def test_obfuscate_json_single_object():
    input_data = json.dumps(
        {"id": 1, "name": "Charlie", "email": "charlie@example.com"}
    )
    pii_fields = ["email"]
    result = obfuscate_json(input_data, pii_fields).decode("utf-8")

    assert "***" in result
    assert "charlie@example.com" not in result
    assert "Charlie" in result  # not obfuscated since name was not targeted


# Missing PII fields (should skip silently)
def test_obfuscate_json_missing_fields():
    input_data = json.dumps({"id": 1, "age": 25})
    pii_fields = ["email", "name"]
    with pytest.raises(ValueError, match="No matching PII fields"):
        obfuscate_json(input_data, pii_fields)


# Invalid JSON format
def test_obfuscate_json_invalid_json():
    bad_json = '{"id": 1, name: "Missing quotes"}'
    with pytest.raises(ValueError):
        obfuscate_json(bad_json, ["name"])


# 	Non-object (e.g., list of strings) → raise ValueError
def test_obfuscate_json_invalid_structure():
    invalid = json.dumps(["string1", "string2"])
    with pytest.raises(ValueError):
        obfuscate_json(invalid, ["name"])


def test_json_field_case_insensitivity():
    input_data = json.dumps({"ID": 1, "Name": "Alice", "Email": "alice@example.com"})
    pii_fields = ["name", "email"]  # Lowercase on purpose

    result = obfuscate_json(input_data, pii_fields).decode("utf-8")

    assert "***" in result
    assert "Alice" not in result
    assert "alice@example.com" not in result


def test_obfuscate_parquet_valid():
    df = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Alice", "Bob"],
            "email": ["alice@example.com", "bob@example.com"],
        }
    )
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine="pyarrow")

    result = obfuscate_parquet(buffer.getvalue(), ["name", "email"])

    df_result = pd.read_parquet(io.BytesIO(result), engine="pyarrow")
    assert all(df_result["name"] == "***")
    assert all(df_result["email"] == "***")
    assert df_result["id"].tolist() == [1, 2]


def test_obfuscate_parquet_invalid_format():
    with pytest.raises(ValueError):
        obfuscate_parquet(b"not a parquet file", ["name"])


def test_parquet_field_case_insensitivity():
    # Create a DataFrame with uppercase column names
    df = pd.DataFrame({"ID": [1], "Name": ["Bob"], "Email": ["bob@example.com"]})

    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine="pyarrow")
    buffer.seek(0)

    pii_fields = ["name", "email"]  # Lowercase

    obfuscated_bytes = obfuscate_parquet(buffer.read(), pii_fields)
    result_df = pd.read_parquet(io.BytesIO(obfuscated_bytes), engine="pyarrow")

    assert result_df["Name"].iloc[0] == "***"
    assert result_df["Email"].iloc[0] == "***"


# def test_obfuscate_handler_json(monkeypatch, s3_bucket):
#     s3 = get_s3_client()

#     data = [
#         {"id": 1, "name": "Alice", "email": "alice@example.com"},
#         {"id": 2, "name": "Bob", "email": "bob@example.com"},
#     ]
#     s3.put_object(
#         Bucket=s3_bucket, Key="data.json", Body=json.dumps(data).encode("utf-8")
#     )

#     input_json = json.dumps(
#         {
#             "file_to_obfuscate": f"s3://{s3_bucket}/data.json",
#             "pii_fields": ["name", "email"],
#         }
#     )

#     result = obfuscate_handler(input_json)
#     assert "***" in result.decode()
#     assert "Alice" not in result.decode()


# def test_obfuscate_handler_parquet(monkeypatch, s3_bucket):
#     df = pd.DataFrame(
#         {
#             "id": [1, 2],
#             "name": ["Alice", "Bob"],
#             "email": ["alice@example.com", "bob@example.com"],
#         }
#     )

#     buffer = io.BytesIO()
#     df.to_parquet(buffer, engine="pyarrow")
#     s3 = get_s3_client()
#     s3.put_object(Bucket=s3_bucket, Key="data.parquet", Body=buffer.getvalue())

#     input_json = json.dumps(
#         {
#             "file_to_obfuscate": f"s3://{s3_bucket}/data.parquet",
#             "pii_fields": ["name", "email"],
#         }
#     )

#     result = obfuscate_handler(input_json)

#     result_df = pd.read_parquet(io.BytesIO(result), engine="pyarrow")
#     assert all(result_df["name"] == "***")
#     assert all(result_df["email"] == "***")
