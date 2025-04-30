import boto3
import pytest

from s3_utils import fetch_file_from_s3
from unittest.mock import patch, MagicMock
from exceptions import S3ObjectNotFoundError

# @patch("boto3.client")
# def test_fetch_file_from_s3(mock_boto):
#     mock_s3 = MagicMock()
#     mock_boto.return_value = mock_s3
#     mock_s3.get_object.return_value = {
#         "Body": MagicMock(read=lambda: b"some,data\n1,2")
#     }
#     result = fetch_file_from_s3("s3://bucket/file.csv")
#     assert result == "some,data\n1,2"


# @mock_s3  # ✅ This is now optional due to conftest.py
# def test_fetch_file_from_s3():
def test_fetch_file_from_s3(s3_bucket):
    s3 = boto3.client("s3", region_name="eu-west-2")
    # bucket = f"test-bucket-{uuid.uuid4()}"
    key = "test.csv"
    test_content = "id,name\n1,Alice"

    # ✅ Required for eu-west-2
    # s3.create_bucket(
    #     Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
    # )

    s3.put_object(Bucket=s3_bucket, Key=key, Body=test_content)

    s3_uri = f"s3://{s3_bucket}/{key}"
    result = fetch_file_from_s3(s3_uri)

    assert result == test_content


# trying to fetch a file that doesn’t exist. Thie code
# Catches ClientError
# Checks if it’s a "NoSuchKey" error
# Raises a clean, readable FileNotFoundError instead.


def test_fetch_file_from_s3_file_not_found(s3_bucket, caplog):
    boto3.client("s3", region_name="eu-west-2")
    key = "missing.csv"
    s3_uri = f"s3://{s3_bucket}/{key}"

    with caplog.at_level("ERROR"):
        with pytest.raises(S3ObjectNotFoundError):
            fetch_file_from_s3(s3_uri)
    assert "Missing file" in caplog.text


# Test Encoding Override (Mocked S3 Read)
# Mocks a UTF-16-encoded file
# Passes an explicit override to decode it
# Confirms the decoded text contains expected content
def test_fetch_file_with_encoding_override():
    fake_s3_uri = "s3://test-bucket/test.csv"
    fake_utf16_content = "id,name\n1,John".encode("utf-16")

    with patch("boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=fake_utf16_content))
        }
        mock_boto.return_value = mock_s3

        result = fetch_file_from_s3(fake_s3_uri, encoding_override="utf-16")
        assert "John" in result
        assert "name" in result


# Test That Logs Encoding Detection
# Simulates an S3 file with a BOM (UTF-8-SIG)
# Captures logs
# Asserts that encoding detection was logged


def test_logs_encoding_detected(caplog):
    fake_s3_uri = "s3://test-bucket/test.csv"
    fake_utf8_bom = b"\xef\xbb\xbfid,name\n1,John"

    with patch("boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=fake_utf8_bom))
        }
        mock_boto.return_value = mock_s3

        with caplog.at_level("INFO"):
            fetch_file_from_s3(fake_s3_uri)

    assert any("Detected file encoding:" in message for message in caplog.messages)
