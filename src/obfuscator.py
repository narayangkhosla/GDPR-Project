# Handles obfuscation of PII fields in CSV:
import csv
import io
from typing import List
import logging

logger = logging.getLogger(__name__)


# def obfuscate_csv(content: str, pii_fields: List[str]) -> bytes:
#     # log events, but not content
#     logger.info("Starting obfuscation of CSV content.")
#     input_buffer = io.StringIO(content)
#     reader = csv.DictReader(input_buffer)

#     if not all(isinstance(f, str) for f in pii_fields):
#         raise TypeError("All field names in pii_fields must be strings.")

#     # Check for valid CSV header
#     # Checks if header exists AND if the content has at least one comma (crude but helpful)
#     # Converts reader to a list to confirm at least 1 row exists
#     if not reader.fieldnames or any("," not in content for _ in range(1)):
#         raise ValueError("Input does not appear to be valid CSV content.")

#     # Additional: Must have at least 1 data row
#     rows = list(reader)
#     # If header exists but no data, just return header
#     if not rows:
#         output_buffer = io.StringIO()
#         writer = csv.DictWriter(output_buffer, fieldnames=reader.fieldnames)
#         writer.writeheader()
#         return output_buffer.getvalue().encode("utf-8")

#     output_buffer = io.StringIO()
#     writer = csv.DictWriter(output_buffer, fieldnames=reader.fieldnames)
#     writer.writeheader()

#     for row in rows:
#         for field in pii_fields:
#             if field in row:
#                 row[field] = "***"
#         writer.writerow(row)

#     return output_buffer.getvalue().encode("utf-8")


def obfuscate_csv(content: str, pii_fields: List[str]) -> bytes:
    # log events, but not content
    logger.info("Starting obfuscation of CSV content.")

    # Early rejection: JSON-style content (starts with { or [)
    if content.strip().startswith("{") or content.strip().startswith("["):
        raise ValueError("Input is not a valid CSV. JSON detected.")

    input_buffer = io.StringIO(content)
    reader = csv.DictReader(input_buffer)

    if not reader.fieldnames or len(reader.fieldnames) < 2:
        raise ValueError("CSV must have at least two columns in the header.")

    output_buffer = io.StringIO()
    writer = csv.DictWriter(output_buffer, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        for field in pii_fields:
            if not isinstance(field, str):
                raise TypeError("All PII field names must be strings.")
            if field in row:
                row[field] = "***"
        writer.writerow(row)

    return output_buffer.getvalue().encode("utf-8")
