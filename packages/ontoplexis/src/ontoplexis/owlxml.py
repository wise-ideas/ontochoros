"""OWL/XML ⇄ property-graph mapping.

OWL/XML is the OWL 2 structural specification serialized as XML, so the
mapping is mechanical rather than per-construct: one element occurrence is one
node, the element name is the node kind, XML attributes are node properties,
and child order is edge position. Named entities merge by (kind, IRI), leaf
values (Literal, IRI, AbbreviatedIRI) merge by content, and anonymous
individuals merge by nodeID; every other element occurrence is its own node.

The mapping is bijective by construction: `serialize_owlxml(parse_owlxml(x))`
reproduces the same element tree, and the round-trip fidelity tests compare
the walker's output against OWLAPI, the reference implementation.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal
from urllib.parse import urljoin, urlsplit

OWL_XMLNS = "http://www.w3.org/2002/07/owl#"
_XML_NS = "http://www.w3.org/XML/1998/namespace"

DbType = Literal["STRING", "INT64"]

# XML attribute (Clark notation for xml:*) <-> node property name.
_ATTR_TO_PROP: dict[str, str] = {
    "IRI": "iri",
    "abbreviatedIRI": "abbreviated_iri",
    "cardinality": "cardinality",
    "nodeID": "node_id",
    "datatypeIRI": "datatype_iri",
    f"{{{_XML_NS}}}lang": "lang",
    "facet": "facet",
    "name": "prefix_name",
    "ontologyIRI": "ontology_iri",
    "versionIRI": "version_iri",
}
_XML_BASE_ATTR = f"{{{_XML_NS}}}base"
# Properties holding full IRIs; relative values resolve against xml:base at
# parse time, so the stored graph is always absolute and base-free.
_IRI_PROPERTIES = frozenset({"iri", "datatype_iri", "ontology_iri", "version_iri", "facet"})
# Serialized attribute names (xml:* written literally; ET emits them verbatim).
_PROP_TO_ATTR: dict[str, str] = {
    "iri": "IRI",
    "abbreviated_iri": "abbreviatedIRI",
    "cardinality": "cardinality",
    "node_id": "nodeID",
    "datatype_iri": "datatypeIRI",
    "lang": "xml:lang",
    "facet": "facet",
    "prefix_name": "name",
    "ontology_iri": "ontologyIRI",
    "version_iri": "versionIRI",
}

#: Every scalar property a node can carry, with its projection column type.
#: `text` holds element text content (Literal values, Import IRIs, …).
SCALAR_PROPERTIES: tuple[tuple[str, DbType], ...] = (
    ("iri", "STRING"),
    ("abbreviated_iri", "STRING"),
    ("node_id", "STRING"),
    ("datatype_iri", "STRING"),
    ("lang", "STRING"),
    ("facet", "STRING"),
    ("prefix_name", "STRING"),
    ("ontology_iri", "STRING"),
    ("version_iri", "STRING"),
    ("text", "STRING"),
    ("cardinality", "INT64"),
)

_ENTITY_KINDS = frozenset(
    {"Class", "Datatype", "ObjectProperty", "DataProperty", "AnnotationProperty", "NamedIndividual"}
)
_VALUE_KINDS = frozenset({"Literal", "IRI", "AbbreviatedIRI"})

# Query-facing role names for a kind's non-annotation children: leading
# positional names, then a repeated name for any remaining children. Roles are
# decoration for Cypher ergonomics; document order (`Edge.position`) is what
# round-trips.
_ROLES: dict[str, tuple[tuple[str, ...], str | None]] = {
    "SubClassOf": (("sub", "super"), None),
    "SubObjectPropertyOf": (("sub", "super"), None),
    "SubDataPropertyOf": (("sub", "super"), None),
    "SubAnnotationPropertyOf": (("sub", "super"), None),
    "EquivalentClasses": ((), "operand"),
    "DisjointClasses": ((), "operand"),
    "EquivalentObjectProperties": ((), "operand"),
    "DisjointObjectProperties": ((), "operand"),
    "EquivalentDataProperties": ((), "operand"),
    "DisjointDataProperties": ((), "operand"),
    "SameIndividual": ((), "operand"),
    "DifferentIndividuals": ((), "operand"),
    "DisjointUnion": (("class",), "operand"),
    "ObjectIntersectionOf": ((), "operand"),
    "ObjectUnionOf": ((), "operand"),
    "ObjectOneOf": ((), "operand"),
    "ObjectComplementOf": (("operand",), None),
    "DataIntersectionOf": ((), "operand"),
    "DataUnionOf": ((), "operand"),
    "DataOneOf": ((), "operand"),
    "DataComplementOf": (("operand",), None),
    "ObjectPropertyChain": ((), "operand"),
    "HasKey": (("class",), "property"),
    "ObjectSomeValuesFrom": (("property", "filler"), None),
    "ObjectAllValuesFrom": (("property", "filler"), None),
    "ObjectHasValue": (("property", "filler"), None),
    "ObjectHasSelf": (("property",), None),
    "ObjectMinCardinality": (("property", "filler"), None),
    "ObjectMaxCardinality": (("property", "filler"), None),
    "ObjectExactCardinality": (("property", "filler"), None),
    "DataSomeValuesFrom": (("property", "filler"), None),
    "DataAllValuesFrom": (("property", "filler"), None),
    "DataHasValue": (("property", "filler"), None),
    "DataMinCardinality": (("property", "filler"), None),
    "DataMaxCardinality": (("property", "filler"), None),
    "DataExactCardinality": (("property", "filler"), None),
    "ObjectInverseOf": (("property",), None),
    "ObjectPropertyDomain": (("property", "domain"), None),
    "ObjectPropertyRange": (("property", "range"), None),
    "DataPropertyDomain": (("property", "domain"), None),
    "DataPropertyRange": (("property", "range"), None),
    "AnnotationPropertyDomain": (("property", "domain"), None),
    "AnnotationPropertyRange": (("property", "range"), None),
    "FunctionalObjectProperty": (("property",), None),
    "InverseFunctionalObjectProperty": (("property",), None),
    "ReflexiveObjectProperty": (("property",), None),
    "IrreflexiveObjectProperty": (("property",), None),
    "SymmetricObjectProperty": (("property",), None),
    "AsymmetricObjectProperty": (("property",), None),
    "TransitiveObjectProperty": (("property",), None),
    "FunctionalDataProperty": (("property",), None),
    "InverseObjectProperties": ((), "property"),
    "ClassAssertion": (("class", "individual"), None),
    "ObjectPropertyAssertion": (("property", "subject", "object"), None),
    "NegativeObjectPropertyAssertion": (("property", "subject", "object"), None),
    "DataPropertyAssertion": (("property", "subject", "object"), None),
    "NegativeDataPropertyAssertion": (("property", "subject", "object"), None),
    "AnnotationAssertion": (("property", "subject", "value"), None),
    "Annotation": (("property", "value"), None),
    "Declaration": (("entity",), None),
    "DatatypeDefinition": (("datatype", "range"), None),
    "DatatypeRestriction": (("datatype",), "facet"),
    "FacetRestriction": (("value",), None),
}


class OwlXmlStructureError(ValueError):
    """Raised when a document or graph violates the OWL/XML mapping contract."""


@dataclass(frozen=True, slots=True)
class Node:
    """One OWL/XML element occurrence (or merged named entity / leaf value)."""

    uid: str
    kind: str
    properties: dict[str, str | int] = field(default_factory=dict, hash=False)

    @property
    def iri(self) -> str | None:
        value = self.properties.get("iri")
        return value if isinstance(value, str) else None


@dataclass(frozen=True, slots=True)
class Edge:
    """A parent→child containment edge; `position` is document order."""

    source: str
    target: str
    position: int
    role: str | None = None


@dataclass(frozen=True, slots=True)
class Graph:
    """A parsed ontology as nodes plus ordered containment edges."""

    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]


def parse_owlxml(text: str) -> Graph:
    """Parse an OWL/XML document into a `Graph`."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise OwlXmlStructureError(f"Not well-formed XML: {exc}") from exc
    if _local(root.tag) != "Ontology":
        raise OwlXmlStructureError(
            f"Expected an <Ontology> root element, got <{_local(root.tag)}>."
        )
    builder = _Builder()
    builder.walk(root)
    return Graph(nodes=tuple(builder.nodes.values()), edges=tuple(builder.edges))


def serialize_owlxml(graph: Graph) -> str:
    """Serialize a `Graph` back to an OWL/XML document string."""
    nodes_by_uid = {node.uid: node for node in graph.nodes}
    children: dict[str, list[Edge]] = defaultdict(list)
    has_parent: set[str] = set()
    for edge in graph.edges:
        if edge.source not in nodes_by_uid:
            raise OwlXmlStructureError(f"Edge source {edge.source!r} is not a node in the graph.")
        if edge.target not in nodes_by_uid:
            raise OwlXmlStructureError(f"Edge target {edge.target!r} is not a node in the graph.")
        children[edge.source].append(edge)
        has_parent.add(edge.target)

    roots = [node for node in graph.nodes if node.kind == "Ontology" and node.uid not in has_parent]
    if len(roots) != 1:
        raise OwlXmlStructureError(
            f"Expected exactly one parentless Ontology node, found {len(roots)}."
        )

    element = _emit(roots[0], nodes_by_uid, children, path=frozenset())
    element.attrib["xmlns"] = OWL_XMLNS
    ET.indent(element)
    return '<?xml version="1.0"?>\n' + ET.tostring(element, encoding="unicode") + "\n"


def role_for(parent_kind: str, child_kind: str, child_index: int) -> str | None:
    """Return the query-facing role for a child, or None when unnamed.

    `child_index` counts non-annotation children only; `Annotation` children
    always take the role "annotation" — including annotations on annotations.
    """
    if child_kind == "Annotation":
        return "annotation"
    if parent_kind == "Ontology":
        return {"Prefix": "prefix", "Import": "import"}.get(child_kind, "axiom")
    leading, rest = _ROLES.get(parent_kind, ((), None))
    if child_index < len(leading):
        return leading[child_index]
    return rest


class _Builder:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self._counter = 0
        self._merged: dict[tuple[str | int | None, ...], str] = {}

    def walk(self, element: ET.Element, base: str | None = None) -> str:
        kind = _local(element.tag)
        own_base = element.attrib.get(_XML_BASE_ATTR)
        if own_base is not None:
            base = urljoin(base, own_base) if base else own_base
        properties = _element_properties(element, kind, base)
        merge_key = _merge_key(kind, properties)
        if merge_key is not None and merge_key in self._merged:
            uid = self._merged[merge_key]
        else:
            uid = f"n{self._counter}"
            self._counter += 1
            self.nodes[uid] = Node(uid=uid, kind=kind, properties=properties)
            if merge_key is not None:
                self._merged[merge_key] = uid

        child_index = 0
        for position, child in enumerate(element):
            child_kind = _local(child.tag)
            child_uid = self.walk(child, base)
            role = role_for(kind, child_kind, child_index)
            if child_kind != "Annotation":
                child_index += 1
            self.edges.append(Edge(source=uid, target=child_uid, position=position, role=role))
        return uid


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _element_properties(element: ET.Element, kind: str, base: str | None) -> dict[str, str | int]:
    properties: dict[str, str | int] = {}
    for attr_name, value in element.attrib.items():
        if attr_name == _XML_BASE_ATTR:
            continue
        prop = _ATTR_TO_PROP.get(attr_name)
        if prop is None:
            raise OwlXmlStructureError(
                f"Unsupported attribute {attr_name!r} on <{kind}>; the OWL/XML "
                "mapping does not know how to store it."
            )
        if prop == "cardinality":
            properties[prop] = int(value)
        elif prop in _IRI_PROPERTIES:
            properties[prop] = _resolve_iri(value, base)
        else:
            properties[prop] = value
    if len(element) == 0:
        raw_text = element.text or ""
        if kind == "Literal":
            properties["text"] = raw_text
        elif raw_text.strip():
            text = raw_text.strip()
            properties["text"] = _resolve_iri(text, base) if kind in ("IRI", "Import") else text
    return properties


def _resolve_iri(value: str, base: str | None) -> str:
    if base is None or urlsplit(value).scheme:
        return value
    return urljoin(base, value)


def _merge_key(kind: str, properties: dict[str, str | int]) -> tuple[str | int | None, ...] | None:
    if kind in _ENTITY_KINDS:
        return (kind, properties.get("iri"), properties.get("abbreviated_iri"))
    if kind == "AnonymousIndividual":
        return (kind, properties.get("node_id"))
    if kind in _VALUE_KINDS:
        return (
            kind,
            properties.get("text"),
            properties.get("datatype_iri"),
            properties.get("lang"),
        )
    return None


def _emit(
    node: Node,
    nodes_by_uid: dict[str, Node],
    children: dict[str, list[Edge]],
    *,
    path: frozenset[str],
) -> ET.Element:
    if node.uid in path:
        raise OwlXmlStructureError(
            f"Cycle through node {node.uid!r} ({node.kind}); OWL/XML documents are trees."
        )
    element = ET.Element(node.kind)
    for prop, attr_name in _PROP_TO_ATTR.items():
        value = node.properties.get(prop)
        if value is not None:
            element.attrib[attr_name] = str(value)
    text = node.properties.get("text")
    if text is not None:
        element.text = str(text)

    child_edges = sorted(children.get(node.uid, []), key=lambda edge: edge.position)
    positions = [edge.position for edge in child_edges]
    if len(set(positions)) != len(positions):
        raise OwlXmlStructureError(
            f"Node {node.uid!r} ({node.kind}) has duplicate child positions: {positions}."
        )
    next_path = path | {node.uid}
    for edge in child_edges:
        element.append(_emit(nodes_by_uid[edge.target], nodes_by_uid, children, path=next_path))
    return element


__all__ = [
    "Edge",
    "Graph",
    "Node",
    "OWL_XMLNS",
    "OwlXmlStructureError",
    "SCALAR_PROPERTIES",
    "parse_owlxml",
    "role_for",
    "serialize_owlxml",
]
