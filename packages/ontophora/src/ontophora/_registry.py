"""Authoritative construct registry for the OWL 2 structural model."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, Annotated, Any, TypeAlias, Union, cast

from pydantic import Field, TypeAdapter
from pydantic.json_schema import JsonSchemaMode

from ontophora.constructs.annotation import (
    Annotation,
    AnnotationProperty,
    AnnotationPropertyDomain,
    AnnotationPropertyRange,
)
from ontophora.constructs.annotation_assertion import (
    AnnotationAssertion,
)
from ontophora.constructs.asymmetric_object_property import AsymmetricObjectProperty
from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.class_assertion import ClassAssertion
from ontophora.constructs.data_all_values_from import DataAllValuesFrom
from ontophora.constructs.data_cardinality import (
    DataExactCardinality,
    DataMaxCardinality,
    DataMinCardinality,
)
from ontophora.constructs.data_complement_of import DataComplementOf
from ontophora.constructs.data_has_value import DataHasValue
from ontophora.constructs.data_intersection_of import DataIntersectionOf
from ontophora.constructs.data_one_of import DataOneOf
from ontophora.constructs.data_property import (
    DataProperty,
    DataPropertyDomain,
    DataPropertyRange,
)
from ontophora.constructs.data_property_assertion import DataPropertyAssertion
from ontophora.constructs.data_some_values_from import DataSomeValuesFrom
from ontophora.constructs.data_union_of import DataUnionOf
from ontophora.constructs.datatype import Datatype
from ontophora.constructs.datatype_definition import DatatypeDefinition
from ontophora.constructs.datatype_restriction import DatatypeRestriction
from ontophora.constructs.declaration import Declaration
from ontophora.constructs.different_individuals import DifferentIndividuals
from ontophora.constructs.disjoint_classes import DisjointClasses
from ontophora.constructs.disjoint_data_properties import DisjointDataProperties
from ontophora.constructs.disjoint_object_properties import DisjointObjectProperties
from ontophora.constructs.disjoint_union import DisjointUnion
from ontophora.constructs.equivalent_classes import EquivalentClasses
from ontophora.constructs.equivalent_data_properties import EquivalentDataProperties
from ontophora.constructs.equivalent_object_properties import EquivalentObjectProperties
from ontophora.constructs.facet_restriction import FacetRestriction
from ontophora.constructs.functional_data_property import FunctionalDataProperty
from ontophora.constructs.functional_object_property import FunctionalObjectProperty
from ontophora.constructs.has_key import HasKey
from ontophora.constructs.individual import AnonymousIndividual, NamedIndividual
from ontophora.constructs.inverse_functional_object_property import (
    InverseFunctionalObjectProperty,
)
from ontophora.constructs.inverse_object_properties import InverseObjectProperties
from ontophora.constructs.inverse_object_property import InverseObjectProperty
from ontophora.constructs.irreflexive_object_property import IrreflexiveObjectProperty
from ontophora.constructs.klass import Klass
from ontophora.constructs.literal import (
    StringLiteralNoLanguage,
    StringLiteralWithLanguage,
    TypedLiteral,
)
from ontophora.constructs.negative_data_property_assertion import (
    NegativeDataPropertyAssertion,
)
from ontophora.constructs.negative_object_property_assertion import (
    NegativeObjectPropertyAssertion,
)
from ontophora.constructs.object_all_values_from import ObjectAllValuesFrom
from ontophora.constructs.object_cardinality import (
    ObjectExactCardinality,
    ObjectMaxCardinality,
    ObjectMinCardinality,
)
from ontophora.constructs.object_complement_of import ObjectComplementOf
from ontophora.constructs.object_has_self import ObjectHasSelf
from ontophora.constructs.object_has_value import ObjectHasValue
from ontophora.constructs.object_intersection_of import ObjectIntersectionOf
from ontophora.constructs.object_one_of import ObjectOneOf
from ontophora.constructs.object_property import (
    ObjectProperty,
    ObjectPropertyDomain,
    ObjectPropertyRange,
)
from ontophora.constructs.object_property_assertion import ObjectPropertyAssertion
from ontophora.constructs.object_some_values_from import ObjectSomeValuesFrom
from ontophora.constructs.object_union_of import ObjectUnionOf
from ontophora.constructs.ontology import DirectlyImportsDocument, Ontology
from ontophora.constructs.ontology_document import OntologyDocument, PrefixDeclaration
from ontophora.constructs.property_expression_chain import PropertyExpressionChain
from ontophora.constructs.reflexive_object_property import ReflexiveObjectProperty
from ontophora.constructs.same_individual import SameIndividual
from ontophora.constructs.sub_annotation_property_of import SubAnnotationPropertyOf
from ontophora.constructs.sub_class_of import SubClassOf
from ontophora.constructs.sub_data_property_of import SubDataPropertyOf
from ontophora.constructs.sub_object_property_of import SubObjectPropertyOf
from ontophora.constructs.symmetric_object_property import SymmetricObjectProperty
from ontophora.constructs.transitive_object_property import TransitiveObjectProperty
from ontophora.reference import model_kind

ConstructType = type[BaseConstruct]
ONTOLOGY_KIND = "Ontology"


@dataclass(frozen=True, slots=True)
class ConstructMetadata:
    kind: str
    model_type: ConstructType
    is_document_construct: bool = False
    is_blank_node: bool = False
    uses_iri_identity: bool = False
    abstract_groups: frozenset[str] = frozenset()


def _metadata(
    model_type: ConstructType,
    *,
    is_document_construct: bool = False,
    is_blank_node: bool = False,
    uses_iri_identity: bool = False,
    abstract_groups: frozenset[str] = frozenset(),
) -> ConstructMetadata:
    return ConstructMetadata(
        kind=model_kind(model_type),
        model_type=model_type,
        is_document_construct=is_document_construct,
        is_blank_node=is_blank_node,
        uses_iri_identity=uses_iri_identity,
        abstract_groups=abstract_groups,
    )


CONSTRUCT_METADATA: tuple[ConstructMetadata, ...] = (
    _metadata(Annotation),
    _metadata(AnnotationAssertion, abstract_groups=frozenset({"Axiom", "AnnotationAxiom"})),
    _metadata(AnnotationProperty, uses_iri_identity=True, abstract_groups=frozenset({"Entity"})),
    _metadata(AnnotationPropertyDomain, abstract_groups=frozenset({"Axiom", "AnnotationAxiom"})),
    _metadata(AnnotationPropertyRange, abstract_groups=frozenset({"Axiom", "AnnotationAxiom"})),
    _metadata(SubAnnotationPropertyOf, abstract_groups=frozenset({"Axiom", "AnnotationAxiom"})),
    _metadata(
        DataProperty,
        uses_iri_identity=True,
        abstract_groups=frozenset({"Entity", "DataPropertyExpression"}),
    ),
    _metadata(Datatype, uses_iri_identity=True, abstract_groups=frozenset({"Entity", "DataRange"})),
    _metadata(
        Klass, uses_iri_identity=True, abstract_groups=frozenset({"Entity", "ClassExpression"})
    ),
    _metadata(
        NamedIndividual,
        uses_iri_identity=True,
        abstract_groups=frozenset({"Individual", "Entity"}),
    ),
    _metadata(
        ObjectProperty,
        uses_iri_identity=True,
        abstract_groups=frozenset({"ObjectPropertyExpression", "Entity"}),
    ),
    _metadata(AnonymousIndividual, abstract_groups=frozenset({"Individual"})),
    _metadata(
        DataAllValuesFrom, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(DataComplementOf, is_blank_node=True, abstract_groups=frozenset({"DataRange"})),
    _metadata(
        DataExactCardinality, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(DataHasValue, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})),
    _metadata(DataIntersectionOf, is_blank_node=True, abstract_groups=frozenset({"DataRange"})),
    _metadata(
        DataMaxCardinality, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(
        DataMinCardinality, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(DataOneOf, is_blank_node=True, abstract_groups=frozenset({"DataRange"})),
    _metadata(
        DataSomeValuesFrom, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(DatatypeRestriction, is_blank_node=True, abstract_groups=frozenset({"DataRange"})),
    _metadata(DataUnionOf, is_blank_node=True, abstract_groups=frozenset({"DataRange"})),
    _metadata(FacetRestriction),
    _metadata(StringLiteralNoLanguage),
    _metadata(StringLiteralWithLanguage),
    _metadata(TypedLiteral),
    _metadata(
        ObjectAllValuesFrom, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(
        ObjectComplementOf, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(
        ObjectExactCardinality, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(ObjectHasSelf, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})),
    _metadata(ObjectHasValue, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})),
    _metadata(
        ObjectIntersectionOf, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(
        ObjectMaxCardinality, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(
        ObjectMinCardinality, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(ObjectOneOf, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})),
    _metadata(
        ObjectSomeValuesFrom, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})
    ),
    _metadata(ObjectUnionOf, is_blank_node=True, abstract_groups=frozenset({"ClassExpression"})),
    _metadata(
        InverseObjectProperty,
        is_blank_node=True,
        abstract_groups=frozenset({"ObjectPropertyExpression"}),
    ),
    _metadata(PropertyExpressionChain),
    _metadata(
        AsymmetricObjectProperty, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})
    ),
    _metadata(ClassAssertion, abstract_groups=frozenset({"Axiom", "Assertion"})),
    _metadata(DataPropertyAssertion, abstract_groups=frozenset({"Axiom", "Assertion"})),
    _metadata(DataPropertyDomain, abstract_groups=frozenset({"Axiom", "DataPropertyAxiom"})),
    _metadata(DataPropertyRange, abstract_groups=frozenset({"Axiom", "DataPropertyAxiom"})),
    _metadata(DatatypeDefinition, abstract_groups=frozenset({"Axiom"})),
    _metadata(Declaration, abstract_groups=frozenset({"Axiom"})),
    _metadata(DifferentIndividuals, abstract_groups=frozenset({"Axiom", "Assertion"})),
    _metadata(DisjointClasses, abstract_groups=frozenset({"Axiom", "ClassAxiom"})),
    _metadata(DisjointDataProperties, abstract_groups=frozenset({"Axiom", "DataPropertyAxiom"})),
    _metadata(
        DisjointObjectProperties, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})
    ),
    _metadata(DisjointUnion, abstract_groups=frozenset({"Axiom", "ClassAxiom"})),
    _metadata(EquivalentClasses, abstract_groups=frozenset({"Axiom", "ClassAxiom"})),
    _metadata(EquivalentDataProperties, abstract_groups=frozenset({"Axiom", "DataPropertyAxiom"})),
    _metadata(
        EquivalentObjectProperties, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})
    ),
    _metadata(FunctionalDataProperty, abstract_groups=frozenset({"Axiom", "DataPropertyAxiom"})),
    _metadata(
        FunctionalObjectProperty, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})
    ),
    _metadata(HasKey, abstract_groups=frozenset({"Axiom"})),
    _metadata(
        InverseFunctionalObjectProperty,
        abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"}),
    ),
    _metadata(InverseObjectProperties, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})),
    _metadata(
        IrreflexiveObjectProperty, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})
    ),
    _metadata(NegativeDataPropertyAssertion, abstract_groups=frozenset({"Axiom", "Assertion"})),
    _metadata(NegativeObjectPropertyAssertion, abstract_groups=frozenset({"Axiom", "Assertion"})),
    _metadata(ObjectPropertyAssertion, abstract_groups=frozenset({"Axiom", "Assertion"})),
    _metadata(ObjectPropertyDomain, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})),
    _metadata(ObjectPropertyRange, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})),
    _metadata(ReflexiveObjectProperty, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})),
    _metadata(SameIndividual, abstract_groups=frozenset({"Axiom", "Assertion"})),
    _metadata(SubClassOf, abstract_groups=frozenset({"Axiom", "ClassAxiom"})),
    _metadata(SubDataPropertyOf, abstract_groups=frozenset({"Axiom", "DataPropertyAxiom"})),
    _metadata(SubObjectPropertyOf, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})),
    _metadata(SymmetricObjectProperty, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})),
    _metadata(
        TransitiveObjectProperty, abstract_groups=frozenset({"Axiom", "ObjectPropertyAxiom"})
    ),
    _metadata(DirectlyImportsDocument, is_document_construct=True),
    _metadata(Ontology),
    _metadata(OntologyDocument, is_document_construct=True),
    _metadata(PrefixDeclaration, is_document_construct=True),
)

construct_types = tuple(metadata.model_type for metadata in CONSTRUCT_METADATA)
construct_metadata = CONSTRUCT_METADATA

if TYPE_CHECKING:
    Construct: TypeAlias = BaseConstruct
else:
    Construct = Annotated[Union[construct_types], Field(discriminator="kind")]  # type: ignore[valid-type]
_construct_adapter = TypeAdapter(Construct)


@lru_cache(maxsize=1)
def construct_metadata_by_kind() -> dict[str, ConstructMetadata]:
    return {metadata.kind: metadata for metadata in CONSTRUCT_METADATA}


def construct(data: dict[str, Any]) -> BaseConstruct:
    return _construct_adapter.validate_python(data)


def construct_json_schema(*, mode: JsonSchemaMode = "validation") -> dict[str, object]:
    return _construct_adapter.json_schema(mode=mode)


@lru_cache(maxsize=2)
def construct_support_manifest(*, mode: JsonSchemaMode = "validation") -> dict[str, object]:
    """Return a JSON-serializable manifest derived from the construct schema.

    This manifest is the schema-driven handoff point for non-Python consumers
    such as the OwlAPI bridge.  It carries the construct kind catalog, per-kind
    field names, and the abstract-group membership already encoded in the
    Python registry.
    """

    schema = construct_json_schema(mode=mode)
    definitions = schema.get("$defs")
    if not isinstance(definitions, dict):
        raise ValueError("construct_json_schema() did not return a $defs mapping")
    definition_map = cast(dict[str, object], definitions)
    one_of = schema.get("oneOf")
    if not isinstance(one_of, list):
        raise ValueError("construct_json_schema() did not return a oneOf list")

    schema_definitions_by_kind: dict[str, dict[str, object]] = {}
    schema_refs: dict[str, str] = {}
    for item in one_of:
        if isinstance(item, dict):
            item_dict = cast(dict[str, object], item)
            ref = item_dict.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/$defs/"):
                definition_name = ref.rsplit("/", 1)[-1]
                definition_obj = definition_map.get(definition_name)
                if not isinstance(definition_obj, dict):
                    continue
                definition = cast(dict[str, object], definition_obj)
                properties_obj = definition.get("properties")
                if not isinstance(properties_obj, dict):
                    continue
                properties = cast(dict[str, object], properties_obj)
                kind_property_obj = properties.get("kind")
                if not isinstance(kind_property_obj, dict):
                    continue
                kind_property = cast(dict[str, object], kind_property_obj)
                kind_value = kind_property.get("const")
                if isinstance(kind_value, str):
                    schema_refs[kind_value] = ref
                    schema_definitions_by_kind[kind_value] = definition

    constructs: dict[str, dict[str, object]] = {}
    groups: dict[str, list[str]] = {}
    for metadata in CONSTRUCT_METADATA:
        definition = schema_definitions_by_kind.get(metadata.kind)
        if not isinstance(definition, dict):
            raise ValueError(f"construct_json_schema() is missing a definition for {metadata.kind}")
        properties = definition.get("properties")
        required = definition.get("required")
        if not isinstance(properties, dict):
            raise ValueError(
                f"construct_json_schema() definition for {metadata.kind} is missing properties"
            )

        field_names = [field_name for field_name in properties if field_name not in {"uid", "kind"}]
        required_fields = [
            field_name
            for field_name in (required if isinstance(required, list) else [])
            if isinstance(field_name, str) and field_name not in {"uid", "kind"}
        ]
        constructs[metadata.kind] = {
            "schema_ref": schema_refs.get(metadata.kind, f"#/$defs/{metadata.kind}"),
            "field_names": field_names,
            "required_fields": required_fields,
            "abstract_groups": sorted(metadata.abstract_groups),
            "is_document_construct": metadata.is_document_construct,
            "is_blank_node": metadata.is_blank_node,
            "uses_iri_identity": metadata.uses_iri_identity,
        }

        for group in metadata.abstract_groups:
            groups.setdefault(group, []).append(metadata.kind)
        if metadata.is_document_construct:
            groups.setdefault("DocumentConstruct", []).append(metadata.kind)
        if metadata.is_blank_node:
            groups.setdefault("BlankNode", []).append(metadata.kind)
        if metadata.uses_iri_identity:
            groups.setdefault("IriIdentity", []).append(metadata.kind)

    return {
        "schema_mode": mode,
        "construct_count": len(constructs),
        "constructs": constructs,
        "groups": {group: sorted(kinds) for group, kinds in sorted(groups.items())},
    }


def is_kind_compatible(*, actual_kind: str, expected_kinds: Iterable[str]) -> bool:
    metadata = construct_metadata_by_kind().get(actual_kind)
    for expected_kind in expected_kinds:
        if actual_kind == expected_kind:
            return True
        if metadata is not None and expected_kind in metadata.abstract_groups:
            return True
    return False


__all__ = [
    "Construct",
    "ConstructMetadata",
    "ConstructType",
    "ONTOLOGY_KIND",
    "construct",
    "construct_json_schema",
    "construct_metadata",
    "construct_metadata_by_kind",
    "construct_support_manifest",
    "construct_types",
    "is_kind_compatible",
]
