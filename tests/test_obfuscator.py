import pytest
from src.obfuscator import obfuscate_csv


def test_obfuscate_csv():
    input_data = "student_id,name,email_address\n123,John Smith,john@example.com"
    pii_fields = ["name", "email_address"]
    output = obfuscate_csv(input_data, pii_fields).decode("utf-8")
    assert "***" in output
    assert "John Smith" not in output
    assert "john@example.com" not in output
