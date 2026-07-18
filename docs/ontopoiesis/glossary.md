---
title: "Glossary"
---

This page collects the project-specific terms used across the Ontopoiesis documentation.

## Ladybug projection

The `.lbug` graph database file produced by `ontopoiesis build`: a queryable encoding of
one OWL 2 document as a labelled property graph. It is not an OWL serialization, and it
should not be stored as a durable artifact between Ontopoiesis versions.

## `.lbug` file

The file extension used for a Ladybug projection. See [Ladybug projection](#ladybug-projection).

## construct

In Ontopoiesis, any OWL 2 structural unit stored as a node in the projection: an axiom, a
class expression, an entity, or an annotation construct. The term comes from the OWL 2
structural specification.

## fingerprint

Also called a semantic fingerprint. A content-addressed key computed from a construct's
structural identity. `ontopoiesis diff` uses fingerprints to compare projections without
depending on storage UIDs, so the same construct receives the same fingerprint across
equivalent serializations.

## UID

An identifier assigned to each node in a projection, in document order (`n0`, `n1`, …).
It is a handle within one built projection but is recomputed on rebuild and not stable
across builds. Use `iri` rather than `uid` for durable external references. (Migrations
use the separate, deterministic `scalar_uid`/`axiom_uid` helpers for `MERGE` idempotence.)

## projection slice

A focused subgraph of a projection containing selected nodes, their immediate structural
context, and optionally one-hop external references. Ontopoiesis uses slices internally as
the input to `ontopoiesis render`.

## Ladybug

The embedded graph database engine used to store and query projections. The
`ontoplexis.graph` layer depends on `real_ladybug` directly.
