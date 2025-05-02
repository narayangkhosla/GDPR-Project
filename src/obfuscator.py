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

    output_buffer = io.StringIO()
    writer = csv.DictWriter(output_buffer, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        for field in pii_fields:
            if not isinstance(field, str):
                raise TypeError("All PII field names must be strings.")
            if field in row:
                row[field] = "***"
                found_fields.add(field)
        writer.writerow(row)

    missing_fields = set(pii_fields) - found_fields

    if not found_fields:
        logger.warning("⚠️ None of the specified PII fields were found in the CSV file.")
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

    found_fields = set()

    def obfuscate_record(record: dict):
        for field in pii_fields:
            if field in record:
                record[field] = "***"
                found_fields.add(field)
        return record

    if isinstance(data, dict):
        obfuscated = obfuscate_record(data)
    elif isinstance(data, list):
        if not all(isinstance(rec, dict) for rec in data):
            raise ValueError("JSON list must contain objects (dicts only).")
        obfuscated = [obfuscate_record(rec) for rec in data]
    else:
        raise ValueError("Unsupported JSON format (must be object or list of objects)")

    missing_fields = set(pii_fields) - found_fields
    if not found_fields:
        logger.warning(
            "⚠️ None of the specified PII fields were found in the JSON data."
        )
        raise ValueError("No matching PII fields found — obfuscation skipped.")

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

    found_fields = set()
    for field in pii_fields:
        if field in df.columns:
            df[field] = "***"
            found_fields.add(field)

    missing_fields = set(pii_fields) - found_fields

    if not found_fields:
        logger.warning(
            "⚠️ None of the specified PII fields were found in the Parquet file."
        )
        raise ValueError("No matching PII fields found — obfuscation skipped.")

    if missing_fields:
        logger.warning(
            f"⚠️ Some PII fields were not found in Parquet: {', '.join(missing_fields)}"
        )

    out_buffer = io.BytesIO()
    df.to_parquet(out_buffer, index=False, engine="pyarrow")

    return out_buffer.getvalue()
