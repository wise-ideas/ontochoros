from typing import Annotated

from pydantic import AfterValidator

NUMBER_OF_BYTES = 4


def _validate_uid(value: str) -> str:
    if not value.startswith(("0x", "0X")):
        raise ValueError(f"Invalid UID: {value}")
    try:
        parsed = int(value, 16)
    except ValueError as exc:
        raise ValueError(f"Invalid UID: {value}") from exc
    return hex(parsed)


# Hex identifier used for construct references in JSON packages.
UID = Annotated[
    str,
    AfterValidator(_validate_uid),
]
