import base64
import re
from typing import Optional, Dict

from tusfastapiserver.exceptions import InvalidMetadataException


ASCII_SPACE = ord(" ")
ASCII_COMMA = ord(",")
BASE64_REGEX = re.compile(r"^[\d+/A-Za-z]*={0,2}$")


def validate_key(key: str) -> bool:
    if len(key) == 0:
        return False

    for char in key:
        char_code_point = ord(char)
        if (
            char_code_point > 127
            or char_code_point == ASCII_SPACE
            or char_code_point == ASCII_COMMA
        ):
            return False

    return True


def validate_value(value: str | None) -> bool:
    if value is None or len(value) % 4 != 0:
        return False

    return bool(BASE64_REGEX.match(value))


def parse(metadata_str: Optional[str]) -> Optional[Dict[str, Optional[str]]]:
    meta = {}

    if not metadata_str:
        return None

    if len(metadata_str.strip()) == 0:
        raise InvalidMetadataException()

    for pair in metadata_str.split(","):
        tokens = pair.split(" ")
        key = tokens[0]
        value = tokens[1] if len(tokens) > 1 else None
        if (
            (len(tokens) == 1 and validate_key(key))
            or (len(tokens) == 2 and validate_key(key) and validate_value(value))
        ) and key not in meta:
            decoded_value = base64.b64decode(value).decode("utf-8") if value else None
            meta[key] = decoded_value
        else:
            raise InvalidMetadataException()

    return meta


def stringify(metadata: Dict[str, Optional[str]]) -> str:
    return ",".join(
        (
            f"{key} {base64.b64encode(value.encode('utf-8')).decode('utf-8')}"
            if value is not None
            else key
        )
        for key, value in metadata.items()
    )
