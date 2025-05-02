# main handler (src/main.py)
import os
import urllib.parse
import argparse
import json
from s3_utils import fetch_file_from_s3, is_valid_s3_uri, get_s3_client
from obfuscator import obfuscate_csv, obfuscate_json, obfuscate_parquet
from exceptions import UnsupportedFormatError
from utils.logging_utils import setup_file_logger
from exceptions import S3ObjectNotFoundError

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

    if s3_uri.lower().endswith(".csv"):
        file_format = "csv"
        binary = False
    elif s3_uri.lower().endswith(".json"):
        file_format = "json"
        binary = False
    elif s3_uri.lower().endswith(".parquet"):
        file_format = "parquet"
        binary = True
    else:
        raise UnsupportedFormatError(
            "Only .csv, .json, and .parquet files are supported."
        )

    file_data = fetch_file_from_s3(s3_uri, encoding_override, binary=binary)

    # 🔍 Check file extension
    if file_format == "csv":
        return obfuscate_csv(file_data, pii_fields)
    elif file_format == "json":
        return obfuscate_json(file_data, pii_fields)
    elif file_format == "parquet":
        return obfuscate_parquet(file_data, pii_fields)
    # return obfuscate_csv(file_data, pii_fields)


# LAMBDA HANDLER

# A basic Lambda setup for this project would:
# Receive an event (e.g., from S3 trigger or Step Function)
# Parse the S3 URI and PII fields from the event payload
# Pass them into obfuscate_handler()
# Return a response (or optionally write back to S3)


def lambda_handler(event, context):
    """
    Lambda handler triggered by an S3 PutObject event.

    Reads the uploaded file, obfuscates it, and writes the result to a new S3 location.
    """
    try:
        # Extract bucket and key from the event
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        s3_uri = f"s3://{bucket}/{key}"

        # Hardcoded for demo: fields to obfuscate
        pii_fields = ["name", "email"]

        # Build JSON payload
        payload = {"file_to_obfuscate": s3_uri, "pii_fields": pii_fields}

        obfuscated_data = obfuscate_handler(json.dumps(payload))

        # Define output location: write to 'obfuscated/' folder in same bucket
        output_key = f"obfuscated/{key.split('/')[-1]}"
        s3 = get_s3_client()

        # Check if the output file already exists
        force = event.get("force")
        if force is None:
            env = os.getenv("ENV", "dev").lower()
            if env == "dev":
                force = True
            else:
                force = os.getenv("FORCE_OVERWRITE", "false").lower() == "true"

        # logger.info(f"Lambda running in ENV={env.upper()}, force={force}")
        logger.info(f"Force overwrite is set to: force={force}")

        if not force:
            try:
                s3.head_object(Bucket=bucket, Key=output_key)
                # If no exception: the object exists → don't overwrite
                logger.warning(
                    "⚠️ Output file already exists at "
                    f"s3://{bucket}/{output_key}. Skipping write."
                )
                return {
                    "statusCode": 409,
                    "body": f"File already exists: s3://{bucket}/{output_key}",
                }
            except s3.exceptions.ClientError as e:
                # If 404 (NoSuchKey), it's okay to write the new file
                if e.response["Error"]["Code"] != "404":
                    raise

        # logger.info(f"📝 Writing obfuscated file to s3://{bucket}/{output_key}")
        # logger.info(f"Obfuscated data: {obfuscated_data[:100]}")  # preview
        s3.put_object(Bucket=bucket, Key=output_key, Body=obfuscated_data)

        logger.info(f"✅ Obfuscated file written to s3://{bucket}/{output_key}")

        return {
            "statusCode": 200,
            "body": f"Obfuscated file written to s3://{bucket}/{output_key}",
        }

    except S3ObjectNotFoundError as e:
        logger.warning(f"Lambda: S3 object not found – {e.bucket}/{e.key}")
        return {"statusCode": 404, "body": str(e)}

    except Exception as e:
        logger.exception("Unexpected error during Lambda execution")
        return {"statusCode": 500, "body": f"Internal server error: {str(e)}"}


############################################


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
            print("=== Obfuscated Data Output ===")
            print(obfuscated_data.decode("utf-8"))
    except S3ObjectNotFoundError as e:
        logger.warning(f"🛑 Skipping - file not found: {e.bucket}/{e.key}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_event = {
        "Records": [
            {"s3": {"bucket": {"name": "test-bucket"}, "object": {"key": "sample.csv"}}}
        ]
    }

    # sys.argv = [
    #     "main.py",
    #     "--s3",
    #     "s3://test-bucket/sample1.csv",
    #     "--fields",
    #     "name",
    #     "email_address",
    # ]
    # sys.argv = [
    #     "main.py",
    #     "--s3",
    #     "s3://test-bucket/sample.json",
    #     "--fields",
    #     "name",
    #     "email_address",
    # ]
    # sys.argv = [
    #     "main.py",
    #     "--s3",
    #     "s3://test-bucket/sample.parquet",
    #     "--fields",
    #     "name",
    #     "email_address",
    #     "--output",
    #     "obfuscated_sample.parquet",
    # ]
    main()
    # print(lambda_handler(test_event, context=None))
