# main handler (src/main.py)
import argparse
import json
from src.s3_utils import fetch_file_from_s3, is_valid_s3_uri
from src.obfuscator import obfuscate_csv
from src.exceptions import UnsupportedFormatError
from src.utils.logging_utils import setup_file_logger
from src.exceptions import S3ObjectNotFoundError

logger = setup_file_logger(__name__, "logs/main.log")


# Fully validated: JSON, required keys, types, format, and extension ✅
def obfuscate_handler(json_input: str, encoding_override: str = None) -> bytes:
    """
    Main handler to process input, fetch the file, and return obfuscated output.

    Args:
        json_input (str): JSON string with 'file_to_obfuscate' and 'pii_fields'.

    Returns:
        bytes: Obfuscated file content as bytes for upload to S3.
    """
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

    file_data = fetch_file_from_s3(s3_uri, encoding_override)
    return obfuscate_csv(file_data, pii_fields)


# -----------------------------
# 🖥️ CLI Demo Code (Optional)
# -----------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Obfuscate PII fields in a CSV file from S3."
    )
    parser.add_argument(
        "--s3",
        required=True,
        help="S3 URI of the input CSV file (e.g., s3://bucket/file.csv)",
    )
    parser.add_argument(
        "--fields", nargs="+", required=True, help="List of PII fields to obfuscate"
    )
    parser.add_argument(
        "--output", help="(Optional) Output file path to save obfuscated result"
    )
    parser.add_argument(
        "--encoding",
        help="(Optional) Force a specific encoding (e.g. utf-8, utf-16, latin-1)",
    )

    args = parser.parse_args()

    input_payload = {"file_to_obfuscate": args.s3, "pii_fields": args.fields}

    try:
        obfuscated_data = obfuscate_handler(
            json.dumps(input_payload), encoding_override=args.encoding
        )

        if args.output:
            with open(args.output, "wb") as f:
                f.write(obfuscated_data)
            print(f"Obfuscated file written to {args.output}")
        else:
            print(obfuscated_data.decode("utf-8").encode().decode("unicode_escape"))
    except S3ObjectNotFoundError as e:
        logger.warning(f"🛑 Skipping – file not found: {e.bucket}/{e.key}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
