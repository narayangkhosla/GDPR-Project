import pytest
from src.main import obfuscate_handler
from src.exceptions import UnsupportedFormatError


# Invalid JSON input
def test_invalid_json_input():
    bad_input = "{file_to_obfuscate: 'missing-quote}"
    with pytest.raises(ValueError):
        obfuscate_handler(bad_input)


# Missing file_to_obfuscate key
def test_missing_file_key():
    input_json = '{"pii_fields": ["email"]}'
    with pytest.raises(KeyError):
        obfuscate_handler(input_json)


# Missing pii_fields key
def test_missing_pii_fields_key():
    input_json = '{"file_to_obfuscate": "s3://bucket/file.csv"}'
    with pytest.raises(KeyError):
        obfuscate_handler(input_json)


# pii_fields is not a list
def test_pii_fields_not_a_list():
    input_json = '{"file_to_obfuscate": "s3://bucket/file.csv", "pii_fields": "email"}'
    with pytest.raises(TypeError):
        obfuscate_handler(input_json)


# Empty pii_fields list
def test_empty_pii_fields_list():
    input_json = '{"file_to_obfuscate": "s3://bucket/file.csv", "pii_fields": []}'
    with pytest.raises(ValueError):
        obfuscate_handler(input_json)


# Empty file_to_obfuscate
def test_empty_file_path():
    input_json = '{"file_to_obfuscate": "", "pii_fields": ["email"]}'
    with pytest.raises(ValueError):
        obfuscate_handler(input_json)


# Bad S3 path format
def test_malformed_s3_uri():
    input_json = '{"file_to_obfuscate": "ftp://invalid/path", "pii_fields": ["email"]}'
    with pytest.raises(ValueError):
        obfuscate_handler(input_json)


def test_file_extension_unsupported_type():
    input_json = (
        '{"file_to_obfuscate": "s3://bucket/file.exe", "pii_fields": ["email"]}'
    )
    with pytest.raises(UnsupportedFormatError):
        obfuscate_handler(input_json)
