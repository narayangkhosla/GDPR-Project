# Downloads CSV content from S3:
import boto3
import re
import os
import chardet
from botocore.exceptions import ClientError
from utils.logging_utils import setup_file_logger
from exceptions import S3ObjectNotFoundError

logger = setup_file_logger(__name__, "logs/s3_utils.log")


def fetch_file_from_s3(
    s3_uri: str, encoding_override: str = None, binary: bool = False
) -> str:
    """
    Fetch a file from an S3 bucket using a boto3 client.

    Args:
        s3_uri (str): The S3 URI in the format s3://bucket/key

    Returns:
        str: The file content as a UTF-8 string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    # endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    endpoint_url = os.getenv("AWS_ENDPOINT_URL", None)

    s3 = boto3.client(
        "s3",
        region_name="eu-west-2",
        endpoint_url=endpoint_url,
        # nosec in lines 34 and 35 tells Bandit to skip security checks on these lines.
        aws_access_key_id="test",  # nosec
        aws_secret_access_key="test",  # nosec
    )

    bucket, key = s3_uri.replace("s3://", "").split("/", 1)
    raw_data = safe_get_s3_object(s3, bucket, key)

    if binary:
        return raw_data  # ✅ return raw bytes as-is for Parquet

    # Use override if provided
    if encoding_override:
        logger.info(f"Using manually specified encoding: {encoding_override}")
        return raw_data.decode(encoding_override)

    # Auto-detect encoding using chardet
    detection = chardet.detect(raw_data)
    encoding = detection.get("encoding", "utf-8")
    confidence = detection.get("confidence", 1.0)

    if confidence < 0.7:
        logger.warning(
            f"⚠️ Low confidence in encoding detection ({confidence:.2f}). "
            "Proceeding with {encoding}."
        )

    logger.info(f"Detected file encoding: {encoding} (confidence: {confidence:.2f})")
    return raw_data.decode(encoding)


def is_valid_s3_uri(uri: str) -> bool:
    pattern = r"^s3://[a-z0-9\-\.]+/.+"
    return re.match(pattern, uri) is not None


def safe_get_s3_object(s3, bucket: str, key: str) -> bytes:
    """
    Attempts to fetch an S3 object, and handles 'NoSuchKey' errors.

    Args:
        s3 (boto3.client): An S3 boto3 client
        bucket (str): Bucket name
        key (str): File key

    Returns:
        bytes: Raw file content

    Raises:
        FileNotFoundError: If the object does not exist
    """
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchKey":
            logger.error(
                f"📁 Missing file: '{key}' in bucket: '{bucket}' "
                "- S3 returned NoSuchKey."
            )
            raise S3ObjectNotFoundError(bucket, key)
        else:
            raise


def get_s3_client() -> boto3.client:
    endpoint_url = os.getenv("AWS_ENDPOINT_URL")

    if endpoint_url:
        print(f"Using LocalStack or custom S3 endpoint: {endpoint_url}")
    else:
        print("Using real AWS S3")
    return boto3.client(
        "s3",
        region_name="eu-west-2",
        endpoint_url=endpoint_url,
        # nosec in lines 34 and 35 tells Bandit to skip security checks on these lines.
        aws_access_key_id="test",  # nosec
        aws_secret_access_key="test",  # nosec
    )
