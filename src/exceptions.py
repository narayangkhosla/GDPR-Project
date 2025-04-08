# Purpose: Clean, readable errors for unsupported formats (.json, .parquet, etc.)


class UnsupportedFormatError(Exception):
    """Raised when the input file format is unsupported."""

    pass


class S3ObjectNotFoundError(Exception):
    """Raised when an S3 object is missing (NoSuchKey)"""

    def __init__(self, bucket, key):
        super().__init__(f"The file '{key}' does not exist in bucket '{bucket}'.")
        self.bucket = bucket
        self.key = key
