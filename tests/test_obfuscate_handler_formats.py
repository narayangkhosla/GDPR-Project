# The purpose is to direct S3 integration tests that simulate a real Lambda-style invocation and verify that the obfuscator:

# ✅ Reads from S3
# ✅ Detects the correct file format
# ✅ Obfuscates the file
# ✅ Writes the obfuscated version back to S3

import json
import pandas as pd
import io
from main import lambda_handler, obfuscate_handler
from s3_utils import get_s3_client


def test_csv_file_obfuscates_successfully(s3_bucket):
    s3 = get_s3_client()
    input_key = "uploads/data.csv"
    output_key = "obfuscated/data.csv"
    s3_uri = f"s3://{s3_bucket}/{input_key}"

    csv_content = (
        "student_id,name,course,email\n"
        "1,John Smith,Software,john.smith@example.com\n"
        "2,Jane Doe,Data Science,jane.doe@example.com\n"
    )

    # Upload CSV to S3
    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=csv_content.encode("utf-8"))

    # Build handler input
    payload = {"file_to_obfuscate": s3_uri, "pii_fields": ["name", "email"]}

    # Call handler
    result_bytes = obfuscate_handler(json.dumps(payload))

    # Save output manually to S3
    s3.put_object(Bucket=s3_bucket, Key=output_key, Body=result_bytes)

    # Validate result
    result = (
        s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode("utf-8")
    )
    assert "***" in result
    assert "john.smith@example.com" not in result
    assert "Jane Doe" not in result


def test_json_file_obfuscates_successfully(s3_bucket):
    s3 = get_s3_client()
    input_key = "uploads/data.json"
    output_key = "obfuscated/data.json"
    s3_uri = f"s3://{s3_bucket}/{input_key}"

    data = [{"id": 1, "name": "Eve", "email": "eve@example.com"}]

    # Upload JSON to S3
    s3.put_object(
        Bucket=s3_bucket, Key=input_key, Body=json.dumps(data).encode("utf-8")
    )

    # Build handler input
    payload = {"file_to_obfuscate": s3_uri, "pii_fields": ["name", "email"]}

    # Run the obfuscation logic directly (not Lambda)
    result_bytes = obfuscate_handler(json.dumps(payload))

    # Save output manually to S3 (MVP spec says caller handles this)
    s3.put_object(Bucket=s3_bucket, Key=output_key, Body=result_bytes)

    # Fetch result and validate
    result = (
        s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode("utf-8")
    )
    assert "***" in result
    assert "eve@example.com" not in result


def test_parquet_file_obfuscates_successfully(s3_bucket):
    s3 = get_s3_client()
    input_key = "uploads/data.parquet"
    output_key = "obfuscated/data.parquet"
    s3_uri = f"s3://{s3_bucket}/{input_key}"

    # Create a small DataFrame
    df = pd.DataFrame(
        {
            "student_id": [1, 2],
            "name": ["John Smith", "Jane Doe"],
            "email": ["john.smith@example.com", "jane.doe@example.com"],
            "course": ["Software", "Data Science"],
        }
    )

    # Save it to Parquet in memory
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False, engine="pyarrow")
    parquet_buffer.seek(0)

    # Upload Parquet to S3
    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=parquet_buffer.read())

    # Build handler input
    payload = {"file_to_obfuscate": s3_uri, "pii_fields": ["name", "email"]}

    # Call handler
    result_bytes = obfuscate_handler(json.dumps(payload))

    # Save output manually to S3
    s3.put_object(Bucket=s3_bucket, Key=output_key, Body=result_bytes)

    # Validate
    result_buffer = io.BytesIO(
        s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read()
    )
    df_result = pd.read_parquet(result_buffer, engine="pyarrow")

    assert all(df_result["name"] == "***")
    assert all(df_result["email"] == "***")


# def test_lambda_json_file_obfuscates_successfully(s3_bucket):
#     s3 = get_s3_client()
#     input_key = "uploads/data.json"
#     output_key = "obfuscated/data.json"
#     data = [{"id": 1, "name": "Eve", "email": "eve@example.com"}]

#     # Upload valid JSON content
#     s3.put_object(
#         Bucket=s3_bucket, Key=input_key, Body=json.dumps(data).encode("utf-8")
#     )

#     event = {
#         "Records": [
#             {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
#         ]
#     }

#     response = lambda_handler(event, context=None)

#     result = (
#         s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode("utf-8")
#     )
#     assert "***" in result
#     assert "eve@example.com" not in result
#     assert response["statusCode"] == 200


# def test_lambda_parquet_file_obfuscates_successfully(s3_bucket):

#     s3 = get_s3_client()
#     input_key = "incoming/data.parquet"
#     output_key = "obfuscated/data.parquet"

#     df = pd.DataFrame({"id": [1], "name": ["Alice"], "email": ["alice@example.com"]})
#     buffer = io.BytesIO()
#     df.to_parquet(buffer, engine="pyarrow")
#     buffer.seek(0)  # reset pointer

#     s3.put_object(Bucket=s3_bucket, Key=input_key, Body=buffer.getvalue())

#     event = {
#         "Records": [
#             {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
#         ]
#     }

#     response = lambda_handler(event, context=None)

#     result = s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read()
#     result_df = pd.read_parquet(io.BytesIO(result), engine="pyarrow")

#     assert all(result_df["name"] == "***")
#     assert all(result_df["email"] == "***")
#     assert response["statusCode"] == 200
