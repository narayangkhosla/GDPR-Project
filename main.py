# main handler (src/main.py)
import json
from src.s3_utils import fetch_file_from_s3
from src.obfuscator import obfuscate_csv


def obfuscate_handler(json_input: str) -> bytes:
    payload = json.loads(json_input)
    s3_uri = payload["file_to_obfuscate"]
    pii_fields = payload["pii_fields"]

    file_data = fetch_file_from_s3(s3_uri)
    return obfuscate_csv(file_data, pii_fields)
