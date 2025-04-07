# Downloads CSV content from S3:
import boto3
import re

from botocore.exceptions import ClientError


def fetch_file_from_s3(s3_uri: str) -> str:
    s3 = boto3.client("s3")
    bucket, key = s3_uri.replace("s3://", "").split("/", 1)
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response["Body"].read().decode("utf-8")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            raise FileNotFoundError(
                f"The file {key} does not exist in bucket {bucket}."
            )
        else:
            raise


def is_valid_s3_uri(uri: str) -> bool:
    pattern = r"^s3://[a-z0-9\-\.]+/.+"
    return re.match(pattern, uri) is not None
