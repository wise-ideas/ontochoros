"""OWL 2 structural-specification models (`ontophora`)."""

from ontophora._registry import (
    construct_json_schema,
    construct_types,
)
from ontophora.constructs.base import BaseConstruct
from ontophora.envelope import EnvelopeError, records_from_json, records_to_json
from ontophora.records import coerce_construct
from ontophora.uid import UID

for _construct_type in construct_types:
    globals()[_construct_type.__name__] = _construct_type

__all__ = [
    "BaseConstruct",
    "EnvelopeError",
    "UID",
    "coerce_construct",
    "construct_json_schema",
    "construct_types",
    "records_from_json",
    "records_to_json",
] + [construct_type.__name__ for construct_type in construct_types]
