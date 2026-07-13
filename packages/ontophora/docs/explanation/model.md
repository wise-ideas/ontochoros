---
title: The model
---

# The model

Ontophora models the OWL 2 structural specification as a set of independent
records. A construct record owns its fields; relationships between records are
UID references instead of nested Pydantic models.

## Records and references

Every construct inherits `uid` and `kind` from `BaseConstruct`. `uid` is a
normalized hexadecimal identifier such as `0x2a`. `kind` is a fixed OWL
construct name such as `Class`, `SubClassOf`, or `ObjectSomeValuesFrom`.

A field that points at another construct has the type `Reference[T]`. At
runtime, it becomes a `ReferenceValue` containing only the target UID. The
generic parameter supplies expected-kind metadata for schema inspection, but
Ontophora deliberately does not resolve the UID or verify that a complete
record set contains it. A package owner can therefore load, stream, index, or
validate records in the order that fits its system.

## The registry is authoritative

The registry contains every concrete model and derives the package-wide
discriminated union from it. That one catalog drives `construct_types`,
`coerce_construct`, and `construct_json_schema`. Adding support for a construct
means adding its model and registering its metadata, not teaching several
separate lists about it.

Metadata also records OWL's abstract categories. For example, `Class` belongs
to `Entity` and `ClassExpression`; `SubClassOf` belongs to `Axiom` and
`ClassAxiom`. Some constructs are marked as blank nodes because they represent
anonymous expressions rather than IRI-identified entities.

## Stable serialization and fingerprints

OWL has both ordered and unordered fields. Models use lists where order carries
meaning and sets where it does not. The base model serializes set values in a
stable order so a model's JSON representation is repeatable.

Fingerprinting goes further: it hashes an acyclic record's content after
replacing each known reference with the referenced record's fingerprint. The
result ignores the record's own UID, so independently assigned identifiers do
not make equal content appear different. References outside the supplied index
remain UID references. Canonical fingerprints for cyclic record graphs are not
yet supported.
