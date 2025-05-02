# Handles obfuscation of PII fields in CSV:
import pandas as pd
import csv
import io
import logging
import json
from typing import List, Union

logger = logging.getLogger(__name__)

# The following function handles:
# Empty values ✅
# Already obfuscated values ✅
# Quoted headers ✅
# Non-string field names ✅
# Skips missing fields (by design) ✅


def obfuscate_csv(content: str, pii_fields: List[str]) -> bytes:
    """
    Obfuscates specified fields in a CSV string and returns the result as bytes.

    Args:
        content (str): The CSV file content as a string.
        pii_fields (List[str]): List of field names to obfuscate.

    Returns:
        bytes: Obfuscated CSV content encoded in UTF-8.

    Raises:
        ValueError: If content is not a valid CSV.
        TypeError: If pii_fields contains non-strings.
    """

    # Early rejection: JSON-style content (starts with { or [)
    if content.strip().startswith("{") or content.strip().startswith("["):
        raise ValueError("Input is not a valid CSV. JSON detected.")

    found_fields = set()
    input_buffer = io.StringIO(content)
    reader = csv.DictReader(input_buffer)

    if not reader.fieldnames or len(reader.fieldnames) < 2:
        raise ValueError("CSV must have at least two columns in the header.")

    # log events, but not content
    logger.info("Starting obfuscation of CSV content.")

    # Normalize header field names and build lookup map
    header_map = {h.lower(): h for h in reader.fieldnames}
    for field in pii_fields:
        if not isinstance(field, str):
            raise TypeError("All PII field names must be strings.")
    pii_fields_normalized = [field.lower() for field in pii_fields]

    output_buffer = io.StringIO()
    writer = csv.DictWriter(output_buffer, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        for field_lower in pii_fields_normalized:
            actual_field = header_map.get(field_lower)
            if actual_field and actual_field in row:
                row[actual_field] = "***"
                found_fields.add(actual_field)
        writer.writerow(row)

    missing_fields = [f for f in pii_fields if f.lower() not in header_map]

    if not found_fields:
        if reader.line_num <= 1:  # Only header processed
            logger.info("ℹ️ No data rows present. Returning header only.")
        else:
            logger.warning(
                "⚠️ None of the specified PII fields were found in the CSV file."
            )
            raise ValueError("No matching PII fields found — obfuscation skipped.")

    if missing_fields:
        logger.warning(f"⚠️ Some PII fields were not found: {', '.join(missing_fields)}")
    return output_buffer.getvalue().encode("utf-8")


# the following function:
# Accepts a JSON string or JSON content from S3
# Replaces values in specified pii_fields with '***'
# Supports:
# Single record (object)
# List of records (list of objects)
# Returns a UTF-8 encoded JSON string as bytes


def obfuscate_json(content: Union[str, bytes], pii_fields: List[str]) -> bytes:
    """
    Obfuscates specified fields in a JSON object or list of objects.

    Args:
        content (str | bytes): JSON string or bytes from S3.
        pii_fields (List[str]): Fields to obfuscate.

    Returns:
        bytes: Obfuscated JSON content encoded as UTF-8.
    """
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON input")

    pii_fields_normalized = [field.lower() for field in pii_fields]
    found_fields = set()

    def obfuscate_record(record: dict):
        lower_record = {k.lower(): k for k in record}
        for pii_field in pii_fields_normalized:
            actual_key = lower_record.get(pii_field)
            if actual_key in record:
                record[actual_key] = "***"
                found_fields.add(actual_key)
        return record

    if isinstance(data, dict):
        obfuscated = obfuscate_record(data)
    elif isinstance(data, list):
        if not all(isinstance(rec, dict) for rec in data):
            raise ValueError("JSON list must contain objects (dicts only).")
        obfuscated = [obfuscate_record(rec) for rec in data]
    else:
        raise ValueError("Unsupported JSON format (must be object or list of objects)")

    if not found_fields:
        logger.warning(
            "⚠️ None of the specified PII fields were found in the JSON data."
        )
        raise ValueError("No matching PII fields found — obfuscation skipped.")

    missing_fields = [
        field
        for field in pii_fields
        if field.lower() not in (key.lower() for key in found_fields)
    ]
    if missing_fields:
        logger.warning(
            f"⚠️ Some PII fields were not found in JSON: {', '.join(missing_fields)}"
        )

    return json.dumps(obfuscated, ensure_ascii=False, indent=2).encode("utf-8")


def obfuscate_parquet(content: Union[bytes, str], pii_fields: List[str]) -> bytes:
    """
    Obfuscates PII fields in a Parquet file and returns as byte stream.

    Args:
        content (bytes): Parquet file content from S3.
        pii_fields (List[str]): List of fields to obfuscate.

    Returns:
        bytes: Obfuscated Parquet file as byte stream.
    """
    logger.info("📦 Inside obfuscate_parquet")
    logger.info(f"Received {len(content)} bytes")

    if isinstance(content, str):
        content = content.encode("utf-8")

    buffer = io.BytesIO(content)
    try:
        df = pd.read_parquet(buffer, engine="pyarrow")
        logger.info(f"📄 Read Parquet: {df.shape[0]} rows, {df.shape[1]} cols")
    except Exception:
        logger.exception("Failed to read parquet")
        raise ValueError("Invalid Parquet format")

    pii_fields_normalized = [field.lower() for field in pii_fields]
    column_map = {col.lower(): col for col in df.columns}

    found_fields = set()

    for field_lower in pii_fields_normalized:
        actual_field = column_map.get(field_lower)
        if actual_field and actual_field in df.columns:
            df[actual_field] = "***"
            found_fields.add(actual_field)

    if not found_fields:
        logger.warning(
            "⚠️ None of the specified PII fields were found in the Parquet file."
        )
        raise ValueError("No matching PII fields found — obfuscation skipped.")

    missing_fields = [field for field in pii_fields if field.lower() not in column_map]
    if missing_fields:
        logger.warning(
            f"⚠️ Some PII fields were not found in Parquet: {', '.join(missing_fields)}"
        )

    out_buffer = io.BytesIO()
    df.to_parquet(out_buffer, index=False, engine="pyarrow")

    return out_buffer.getvalue()
