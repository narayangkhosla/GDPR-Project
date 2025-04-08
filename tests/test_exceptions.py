import pytest
from src.exceptions import S3ObjectNotFoundError


# ✅Initialization, message content, attributes
def test_s3_object_not_found_error_message():
    exc = S3ObjectNotFoundError("my-bucket", "missing.csv")
    assert isinstance(exc, Exception)
    assert isinstance(exc, S3ObjectNotFoundError)
    assert exc.bucket == "my-bucket"
    assert exc.key == "missing.csv"
    assert str(exc) == "The file 'missing.csv' does not exist in bucket 'my-bucket'."


# ✅It behaves like a proper exception
def test_s3_object_not_found_error_raises():
    with pytest.raises(S3ObjectNotFoundError) as exc_info:
        raise S3ObjectNotFoundError("bucket-x", "file.csv")

    exc = exc_info.value
    assert exc.bucket == "bucket-x"
    assert exc.key == "file.csv"
    assert "does not exist" in str(exc)
