# The purpose is to direct S3 integration tests that simulate a real Lambda-style invocation and verify that the obfuscator:

# ✅ Reads from S3
# ✅ Detects the correct file format
# ✅ Obfuscates the file
# ✅ Writes the obfuscated version back to S3

import json
import pandas as pd
import io
from src.main import lambda_handler
from src.s3_utils import get_s3_client


def test_lambda_json_file_obfuscates_successfully(s3_bucket):
    s3 = get_s3_client()
    input_key = "uploads/data.json"
    output_key = "obfuscated/data.json"
    data = [{"id": 1, "name": "Eve", "email": "eve@example.com"}]

    # Upload valid JSON content
    s3.put_object(
        Bucket=s3_bucket, Key=input_key, Body=json.dumps(data).encode("utf-8")
    )

    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ]
    }

    response = lambda_handler(event, context=None)

    result = (
        s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read().decode("utf-8")
    )
    assert "***" in result
    assert "eve@example.com" not in result
    assert response["statusCode"] == 200


def test_lambda_parquet_file_obfuscates_successfully(s3_bucket):

    s3 = get_s3_client()
    input_key = "incoming/data.parquet"
    output_key = "obfuscated/data.parquet"

    df = pd.DataFrame({"id": [1], "name": ["Alice"], "email": ["alice@example.com"]})
    buffer = io.BytesIO()
    df.to_parquet(buffer, engine="pyarrow")
    buffer.seek(0)  # reset pointer

    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=buffer.getvalue())

    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ]
    }

    response = lambda_handler(event, context=None)

    result = s3.get_object(Bucket=s3_bucket, Key=output_key)["Body"].read()
    result_df = pd.read_parquet(io.BytesIO(result), engine="pyarrow")

    assert all(result_df["name"] == "***")
    assert all(result_df["email"] == "***")
    assert response["statusCode"] == 200
