import boto3
import pytest

from moto import mock_aws
from src.s3_utils import fetch_file_from_s3
from botocore.exceptions import ClientError

# from unittest.mock import patch, MagicMock


# @patch("boto3.client")
# def test_fetch_file_from_s3(mock_boto):
#     mock_s3 = MagicMock()
#     mock_boto.return_value = mock_s3
#     mock_s3.get_object.return_value = {
#         "Body": MagicMock(read=lambda: b"some,data\n1,2")
#     }
#     result = fetch_file_from_s3("s3://bucket/file.csv")
#     assert result == "some,data\n1,2"


@mock_aws
def test_fetch_file_from_s3():
    # Setup
    s3 = boto3.client("s3", region_name="eu-west-2")
    bucket = "test-bucket"
    key = "test.csv"
    test_content = "id,name\n1,Alice"

    # Create mock bucket and upload file
    s3.create_bucket(
        Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
    )

    s3.put_object(Bucket=bucket, Key=key, Body=test_content)

    # Act
    s3_uri = f"s3://{bucket}/{key}"
    result = fetch_file_from_s3(s3_uri)

    # Assert
    assert result == test_content


# trying to fetch a file that doesn’t exist. Thie code
# Catches ClientError
# Checks if it’s a "NoSuchKey" error
# Raises a clean, readable FileNotFoundError instead.

# @mock_aws
# def test_fetch_file_from_s3_file_not_found():
#     s3 = boto3.client("s3", region_name="eu-west-2")
#     bucket = "test-bucket"
#     key = "missing.csv"

#     # Create bucket without uploading any file
#     s3.create_bucket(
#         Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
#     )

#     s3_uri = f"s3://{bucket}/{key}"

#     # Expect a ClientError when file is missing
#     with pytest.raises(ClientError) as exc_info:
#         fetch_file_from_s3(s3_uri)

#     assert "NoSuchKey" in str(exc_info.value)


@mock_aws
def test_fetch_file_from_s3_file_not_found():
    s3 = boto3.client("s3", region_name="eu-west-2")
    bucket = "test-bucket"
    key = "missing.csv"

    s3.create_bucket(
        Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
    )

    s3_uri = f"s3://{bucket}/{key}"

    with pytest.raises(FileNotFoundError) as exc_info:
        fetch_file_from_s3(s3_uri)

    assert "does not exist" in str(exc_info.value)
