"""OWL/XML ⇄ property-graph mapping.

OWL/XML is the OWL 2 structural specification serialized as XML, so the
mapping is mechanical rather than per-construct: one element occurrence is one
node, the element name is the node kind, XML attributes are node properties,
and child order is edge position. Named entities merge by (kind, IRI), leaf
values (Literal, IRI) merge by content, and anonymous individuals merge by
nodeID; every other element occurrence is its own node.

Abbreviated IRIs are resolved to full IRIs at parse time against the document's
`<Prefix>` declarations: an `abbreviatedIRI` attribute becomes an `iri`
property and an `<AbbreviatedIRI>` leaf becomes an `IRI` value. The stored graph
therefore carries one identity representation, so a term referenced both ways
is a single node. This preserves the functional-syntax round-trip contract
(prefix form is not observable there) while making entity identity uniform.

The mapping is bijective by construction: `serialize_owlxml(parse_owlxml(x))`
reproduces the same element tree, and the round-trip fidelity tests compare
the walker's output against OWLAPI, the reference implementation.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
import xml.parsers.expat
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal
from urllib.parse import urljoin, urlsplit

OWL_XMLNS = "http://www.w3.org/2002/07/owl#"
_OWL_TAG_PREFIX = f"{{{OWL_XMLNS}}}"
_XML_NS = "http://www.w3.org/XML/1998/namespace"

DbType = Literal["STRING", "INT64"]

# XML attribute (Clark notation for xml:*) <-> node property name. The
# `abbreviatedIRI` attribute is handled separately (resolved to `iri`), so it is
# absent here.
_ATTR_TO_PROP: dict[str, str] = {
    "IRI": "iri",
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
# `AbbreviatedIRI` leaves are remapped to `IRI` during the walk, so only these
# two value kinds ever reach the merge table.
_VALUE_KINDS = frozenset({"Literal", "IRI"})

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

# Kinds whose children take roles by child kind rather than by position:
# OWL 2's n-ary data restrictions hold one or more data property expressions
# followed by a data range, so the property count is variable. A data property
# expression is always a named DataProperty and no data range kind is, so the
# child kind discriminates exactly. Value: (role by child kind, default role).
_ROLES_BY_CHILD_KIND: dict[str, tuple[dict[str, str], str]] = {
    "DataSomeValuesFrom": ({"DataProperty": "property"}, "filler"),
    "DataAllValuesFrom": ({"DataProperty": "property"}, "filler"),
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


class _PrologClean(Exception):
    """Sentinel: the prolog was scanned up to the root element with no DTD."""


def _reject_doctype(text: str) -> None:
    """Refuse documents carrying a DTD, before handing them to ElementTree.

    OWL/XML never needs a document type declaration, and rejecting DOCTYPE
    outright closes both entity-expansion (billion-laughs) and external-entity
    (XXE) vectors regardless of the underlying parser's defaults. A DOCTYPE can
    only appear in the prolog, so the scan aborts at the root element and costs
    nothing on the document body.
    """

    def forbid(*_args: object) -> None:
        raise OwlXmlStructureError(
            "Document type declarations (<!DOCTYPE ...>) are not allowed in OWL/XML input."
        )

    def stop(*_args: object) -> None:
        raise _PrologClean

    parser = xml.parsers.expat.ParserCreate()
    parser.StartDoctypeDeclHandler = forbid
    parser.StartElementHandler = stop
    try:
        parser.Parse(text, True)
    except _PrologClean:
        return
    except xml.parsers.expat.ExpatError:
        return  # not well-formed: fall through so ElementTree reports it


def parse_owlxml(text: str) -> Graph:
    """Parse an OWL/XML document into a `Graph`."""
    _reject_doctype(text)
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise OwlXmlStructureError(f"Not well-formed XML: {exc}") from exc
    if _local(root.tag) != "Ontology":
        raise OwlXmlStructureError(
            f"Expected an <Ontology> root element, got <{_local(root.tag)}>."
        )
    builder = _Builder(prefixes=_collect_prefixes(root, root.attrib.get(_XML_BASE_ATTR)))
    builder.walk(root)
    return Graph(nodes=tuple(builder.nodes.values()), edges=tuple(builder.edges))


def _collect_prefixes(root: ET.Element, base: str | None) -> dict[str, str]:
    """Map prefix name (``""`` for the default) to namespace IRI.

    `<Prefix>` declarations are direct children of `<Ontology>`, so the whole map
    is known before any abbreviated IRI in the body is resolved. Namespace IRIs
    resolve against xml:base exactly like direct IRI attributes do, so both
    reference forms of a term land on the same absolute IRI.
    """
    prefixes: dict[str, str] = {}
    for child in root:
        if _local(child.tag) != "Prefix":
            continue
        name = child.attrib.get("name", "")
        namespace = child.attrib.get("IRI")
        if namespace is None:
            raise OwlXmlStructureError(f"<Prefix name={name!r}> is missing its IRI attribute.")
        if name in prefixes:
            raise OwlXmlStructureError(f"Prefix {name!r} is declared more than once.")
        child_base = child.attrib.get(_XML_BASE_ATTR)
        if child_base is not None:
            child_base = urljoin(base, child_base) if base else child_base
        prefixes[name] = _resolve_iri(namespace, child_base if child_base is not None else base)
    return prefixes


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

    visited: set[str] = set()
    element = _emit(roots[0], nodes_by_uid, children, path=frozenset(), visited=visited)
    unreachable = sorted(set(nodes_by_uid) - visited)
    if unreachable:
        raise OwlXmlStructureError(
            "Nodes unreachable from the Ontology root would be silently dropped: "
            f"{', '.join(unreachable[:10])}."
        )
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
    kind_roles = _ROLES_BY_CHILD_KIND.get(parent_kind)
    if kind_roles is not None:
        role_by_child_kind, default_role = kind_roles
        return role_by_child_kind.get(child_kind, default_role)
    leading, rest = _ROLES.get(parent_kind, ((), None))
    if child_index < len(leading):
        return leading[child_index]
    return rest


class _Builder:
    def __init__(self, prefixes: dict[str, str]) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self._counter = 0
        self._merged: dict[tuple[str | int | None, ...], str] = {}
        self._prefixes = prefixes

    def walk(self, element: ET.Element, base: str | None = None) -> str:
        if not element.tag.startswith(_OWL_TAG_PREFIX):
            raise OwlXmlStructureError(
                f"Element <{_local(element.tag)}> is not in the OWL/XML namespace "
                f"{OWL_XMLNS}; a document in another vocabulary cannot be mapped."
            )
        raw_kind = _local(element.tag)
        own_base = element.attrib.get(_XML_BASE_ATTR)
        if own_base is not None:
            base = urljoin(base, own_base) if base else own_base
        properties = _element_properties(element, raw_kind, base, self._prefixes)
        # An abbreviated-IRI leaf denotes the same thing as an <IRI> leaf, so it
        # is stored as one; entity refs keep their element kind (identity moved
        # from the abbreviatedIRI attribute to the resolved `iri` property).
        kind = "IRI" if raw_kind == "AbbreviatedIRI" else raw_kind
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


def _element_properties(
    element: ET.Element, kind: str, base: str | None, prefixes: dict[str, str]
) -> dict[str, str | int]:
    properties: dict[str, str | int] = {}
    if "IRI" in element.attrib and "abbreviatedIRI" in element.attrib:
        raise OwlXmlStructureError(
            f"<{kind}> carries both IRI and abbreviatedIRI attributes; "
            "entity identity must be given exactly once."
        )
    for attr_name, value in element.attrib.items():
        if attr_name == _XML_BASE_ATTR:
            continue
        if attr_name == "abbreviatedIRI":
            properties["iri"] = _resolve_curie(value, prefixes)
            continue
        prop = _ATTR_TO_PROP.get(attr_name)
        if prop is None:
            raise OwlXmlStructureError(
                f"Unsupported attribute {attr_name!r} on <{kind}>; the OWL/XML "
                "mapping does not know how to store it."
            )
        if prop == "cardinality":
            try:
                properties[prop] = int(value)
            except ValueError as exc:
                raise OwlXmlStructureError(
                    f"Attribute cardinality={value!r} on <{kind}> is not an integer."
                ) from exc
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
            if kind == "AbbreviatedIRI":
                properties["text"] = _resolve_curie(text, prefixes)
            elif kind in ("IRI", "Import"):
                properties["text"] = _resolve_iri(text, base)
            else:
                properties["text"] = text
    else:
        stray = [element.text or "", *(child.tail or "" for child in element)]
        if any(s.strip() for s in stray):
            raise OwlXmlStructureError(
                f"<{kind}> mixes text content with child elements; the OWL/XML "
                "mapping cannot store it."
            )
    return properties


def _resolve_iri(value: str, base: str | None) -> str:
    if base is None or urlsplit(value).scheme:
        return value
    # The reference implementation (OWLAPI) resolves relative IRIs in OWL/XML
    # by concatenating the in-scope xml:base with the value, not by RFC 3986
    # reference resolution — RFC resolution would drop the trailing segment of
    # a base ending in '#', turning owl# + maxQualifiedCardinality into
    # .../07/maxQualifiedCardinality. Fidelity is defined by the reference
    # implementation, so match it.
    return base + value


def _resolve_curie(value: str, prefixes: dict[str, str]) -> str:
    """Expand a ``prefix:local`` abbreviated IRI against the prefix map."""
    name, _, local = value.partition(":")
    namespace = prefixes.get(name)
    if namespace is None:
        raise OwlXmlStructureError(f"Abbreviated IRI {value!r} uses undeclared prefix {name!r}.")
    return namespace + local


def _merge_key(kind: str, properties: dict[str, str | int]) -> tuple[str | int | None, ...] | None:
    if kind in _ENTITY_KINDS:
        return (kind, properties.get("iri"))
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
    visited: set[str],
) -> ET.Element:
    if node.uid in path:
        raise OwlXmlStructureError(
            f"Cycle through node {node.uid!r} ({node.kind}); OWL/XML documents are trees."
        )
    visited.add(node.uid)
    element = ET.Element(node.kind)
    for prop, attr_name in _PROP_TO_ATTR.items():
        value = node.properties.get(prop)
        if value is not None:
            element.attrib[attr_name] = str(value)
    text = node.properties.get("text")
    if text is not None:
        element.text = str(text)

    child_edges = sorted(children.get(node.uid, []), key=lambda edge: edge.position)
    if text is not None and child_edges:
        raise OwlXmlStructureError(
            f"Node {node.uid!r} ({node.kind}) mixes text content with child edges; "
            "the OWL/XML mapping cannot serialize it."
        )
    positions = [edge.position for edge in child_edges]
    if len(set(positions)) != len(positions):
        raise OwlXmlStructureError(
            f"Node {node.uid!r} ({node.kind}) has duplicate child positions: {positions}."
        )
    next_path = path | {node.uid}
    for edge in child_edges:
        element.append(
            _emit(
                nodes_by_uid[edge.target], nodes_by_uid, children, path=next_path, visited=visited
            )
        )
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
