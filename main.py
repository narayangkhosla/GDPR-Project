# main handler (src/main.py)
import json
from src.s3_utils import fetch_file_from_s3, is_valid_s3_uri
from src.obfuscator import obfuscate_csv
from src.exceptions import UnsupportedFormatError


def obfuscate_handler(json_input: str) -> bytes:
    try:
        payload = json.loads(json_input)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON input.")

    if "file_to_obfuscate" not in payload:
        raise KeyError("Missing 'file_to_obfuscate'.")
    if not payload["file_to_obfuscate"]:
        raise ValueError("Empty 'file_to_obfuscate'.")

    # KeyError raised when the key is missing
    # ValueError or TypeError raised only when values are present but invalid
    if "pii_fields" not in payload:
        raise KeyError("Missing 'pii_fields'.")
    if not isinstance(payload["pii_fields"], list):
        raise TypeError("'pii_fields' must be a list.")
    if not payload["pii_fields"]:
        raise ValueError("'pii_fields' cannot be empty.")

    s3_uri = payload["file_to_obfuscate"]
    pii_fields = payload["pii_fields"]

    if not is_valid_s3_uri(s3_uri):
        raise ValueError("Invalid S3 URI format.")

    # 🔍 Check file extension
    if not s3_uri.lower().endswith(".csv"):
        raise UnsupportedFormatError("Only .csv files are currently supported.")

    file_data = fetch_file_from_s3(s3_uri)
    return obfuscate_csv(file_data, pii_fields)
