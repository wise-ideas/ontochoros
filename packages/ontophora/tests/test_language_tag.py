import pytest
from pydantic import TypeAdapter, ValidationError

from ontophora.constructs.types import LanguageTag

LANGUAGE_TAG_ADAPTER = TypeAdapter(LanguageTag)


# These edge cases are pinned to the current language-tags runtime behavior,
# not the full set of tags that RFC 5646 would consider well-formed/valid.
@pytest.mark.parametrize(
    "value",
    [
        "@en",
        "@fr",
        "@en-us",
        "@en-US",
        "@zh-Hant",
        "@de-CH-1901",
        "@en-a-bbb-x-a1",
        "@es-419",
        "@i-default",
    ],
)
def test_language_tag_accepts_valid_langtags(value: str) -> None:
    assert LANGUAGE_TAG_ADAPTER.validate_python(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "@",
        "en-US",
        "@en-abcdefghi",
        "@nl-BE-BE",
        "@de-419-DE-alt",
        "@sl-rozaj-biske",
        "@x-private",
        "@sgn-US",
    ],
)
def test_language_tag_rejects_invalid_langtags(value: str) -> None:
    with pytest.raises(ValidationError):
        LANGUAGE_TAG_ADAPTER.validate_python(value)
