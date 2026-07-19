"""Contract tests for LanguageTag: shape and delegation, not the registry.

Validity is delegated to the language-tags runtime (BCP 47 registry data),
which this package does not own. Pinning that library's edge-case verdicts
here would break on every upgrade without telling us anything about our own
code, so these tests cover only the contract that is ours: the leading-@
framing, and that clearly-valid/clearly-invalid tags pass through delegation.
"""

import pytest
from pydantic import TypeAdapter, ValidationError

from ontophora.constructs.types import LanguageTag

LANGUAGE_TAG_ADAPTER = TypeAdapter(LanguageTag)


@pytest.mark.parametrize("value", ["@en", "@en-US", "@zh-Hant", "@es-419"])
def test_language_tag_accepts_common_valid_langtags_verbatim(value: str) -> None:
    assert LANGUAGE_TAG_ADAPTER.validate_python(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "",  # no framing at all
        "@",  # framing without a tag
        "en-US",  # missing the leading @
        "@en-abcdefghi",  # delegated: subtag too long to be well-formed
    ],
)
def test_language_tag_rejects_malformed_values(value: str) -> None:
    with pytest.raises(ValidationError):
        LANGUAGE_TAG_ADAPTER.validate_python(value)
