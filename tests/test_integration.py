# Purpose
# Let’s build a unit-style test that:
# Uploads a real CSV to a mock S3
# Calls the obfuscation handler
# Downloads the result
# Confirms the PII was correctly obfuscated

from main import lambda_handler
from s3_utils import get_s3_client

# Mocks input file upload to S3
# Triggers the lambda_handler() like a real S3 event
# Reads back the output
# Asserts that:
# PII fields are fully obfuscated
# Output is written to correct key (obfuscated/sample.csv)
# Response is 200 OK


def test_lambda_obfuscates_and_saves_to_s3(s3_bucket):
    s3 = get_s3_client()
    input_key = "sample.csv"
    output_key = "obfuscated/sample.csv"

    # Original CSV content
    csv_content = "id,name,email\n1,John,john@example.com\n2,Jane,jane@example.com"

    # Upload the sample file to mocked S3
    s3.put_object(Bucket=s3_bucket, Key=input_key, Body=csv_content)

    # Simulate an S3 event
    event = {
        "Records": [
            {"s3": {"bucket": {"name": s3_bucket}, "object": {"key": input_key}}}
        ]
    }

    # Run the Lambda handler
    response = lambda_handler(event, context=None)

    # Download the obfuscated output
    result = s3.get_object(Bucket=s3_bucket, Key=output_key)
    obfuscated_content = result["Body"].read().decode("utf-8")

    # Check output format and obfuscation
    assert "John" not in obfuscated_content
    assert "jane@example.com" not in obfuscated_content
    assert obfuscated_content.count("***") == 4
    assert "id" in obfuscated_content
    assert response["statusCode"] == 200
