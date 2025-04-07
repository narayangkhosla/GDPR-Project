# Handles obfuscation of PII fields in CSV:
import csv
import io
from typing import List


def obfuscate_csv(content: str, pii_fields: List[str]) -> bytes:
    input_buffer = io.StringIO(content)
    reader = csv.DictReader(input_buffer)

    output_buffer = io.StringIO()
    writer = csv.DictWriter(output_buffer, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        for field in pii_fields:
            if field in row:
                row[field] = "***"
        writer.writerow(row)

    return output_buffer.getvalue().encode("utf-8")
