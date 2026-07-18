import re
from typing import Annotated

from pydantic import AfterValidator

NUMBER_OF_BYTES = 4

_UID_RE = re.compile(r"0[xX][0-9A-Fa-f]+")


def _validate_uid(value: str) -> str:
    # int(value, 16) alone is too lenient: it accepts underscores and
    # surrounding whitespace, which are not valid in the wire form.
    if _UID_RE.fullmatch(value) is None:
        raise ValueError(f"Invalid UID: {value}")
    return hex(int(value, 16))


# Hex identifier used for construct references in JSON packages.
UID = Annotated[
    str,
    AfterValidator(_validate_uid),
]
