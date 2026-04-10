import base64
import json
from typing import Any


def decode_base64_json(value: str) -> dict[str, Any]:
    """Decode a base64-encoded JSON payload into a dictionary."""
    decoded_bytes = base64.b64decode(value)
    decoded_string = decoded_bytes.decode("utf-8")
    return json.loads(decoded_string)


__all__ = ["decode_base64_json"]
