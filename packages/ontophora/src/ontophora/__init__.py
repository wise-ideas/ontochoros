"""OWL 2 structural-specification models (`ontophora`)."""

from ontophora._registry import (
    ONTOLOGY_KIND,
    Construct,
    ConstructMetadata,
    construct_json_schema,
    construct_metadata,
    construct_metadata_by_kind,
    construct_types,
)
from ontophora.constructs.base import BaseConstruct
from ontophora.display import (
    compact_display_label,
    compact_display_value,
    construct_display_iri,
    construct_display_label,
)
from ontophora.envelope import EnvelopeError, records_from_json, records_to_json
from ontophora.fingerprint import fingerprint_construct, fingerprint_constructs
from ontophora.records import coerce_construct, coerce_construct_records
from ontophora.reference import Reference, ReferenceValue, model_kind
from ontophora.reference_inspection import ReferenceEntry, iter_construct_references
from ontophora.uid import UID

for _construct_type in construct_types:
    globals()[_construct_type.__name__] = _construct_type

__all__ = [
    "BaseConstruct",
    "Construct",
    "ConstructMetadata",
    "EnvelopeError",
    "ONTOLOGY_KIND",
    "Reference",
    "ReferenceEntry",
    "ReferenceValue",
    "UID",
    "coerce_construct",
    "coerce_construct_records",
    "compact_display_label",
    "compact_display_value",
    "construct_display_iri",
    "construct_display_label",
    "construct_json_schema",
    "construct_metadata",
    "construct_metadata_by_kind",
    "construct_types",
    "fingerprint_construct",
    "fingerprint_constructs",
    "iter_construct_references",
    "model_kind",
    "records_from_json",
    "records_to_json",
] + [construct_type.__name__ for construct_type in construct_types]
