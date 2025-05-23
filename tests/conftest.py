import sys
import os
import logging
import pytest
import uuid
import boto3
from moto import mock_s3


@pytest.fixture(autouse=True)
def configure_logging():
    logging.basicConfig(level=logging.INFO)


@pytest.fixture(autouse=True)
def reset_s3():
    with mock_s3():
        yield


# To ensure fetch_file_from_s3() uses moto's mocked AWS, not LocalStack.


@pytest.fixture(autouse=True)
def unset_localstack(monkeypatch):
    monkeypatch.delenv("AWS_ENDPOINT_URL", raising=False)


@pytest.fixture
def s3_bucket():
    bucket = f"test-bucket-{uuid.uuid4()}"
    s3 = boto3.client("s3", region_name="eu-west-2")
    s3.create_bucket(
        Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
    )
    return bucket


@pytest.fixture(autouse=True)
def set_default_env(monkeypatch):
    monkeypatch.setenv("ENV", "dev")


# Add src/ to sys.path at runtime
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
