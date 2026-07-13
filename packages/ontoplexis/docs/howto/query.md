---
title: Query a Projection
---

# Query a Projection

## Get a projection

```python
from ontoplexis import Ontology, Projection

ont = Ontology.from_owlxml(path.read_text())
proj = ont.project()                        # in-memory (temp file)
proj = ont.save_projection("onto.lbug")     # durable
proj = Projection.open("onto.lbug")         # reload
```

`Projection` is a context manager; use `with … as proj:` or call `close()`.

## Execute Cypher

```python
rows = proj.execute(
    "MATCH (n:N {kind: 'Class'}) WHERE n.iri IS NOT NULL "
    "RETURN n.iri AS iri ORDER BY iri"
)
```

`execute` returns `list[dict]`; column names are your `RETURN` aliases. Use
`$parameters` instead of string interpolation:

```python
proj.execute(
    "MATCH (n:N {iri: $iri})<-[:E]-(parent:N) RETURN parent.kind AS kind",
    parameters={"iri": "http://example.org/animals#Dog"},
)
```

## Common patterns

Direct subclass pairs:

```cypher
MATCH (a:N)<-[:E {role:'sub'}]-(:N {kind:'SubClassOf'})-[:E {role:'super'}]->(b:N)
WHERE a.iri IS NOT NULL AND b.iri IS NOT NULL
RETURN a.iri AS sub_iri, b.iri AS super_iri
```

Everything that mentions an entity (impact seed):

```cypher
MATCH (x:N {iri: $iri})<-[:E]-(user:N)
RETURN DISTINCT user.kind AS kind, user.uid AS uid
```

Labels:

```cypher
MATCH (aa:N {kind:'AnnotationAssertion'})-[:E {role:'property'}]->(:N {abbreviated_iri:'rdfs:label'}),
      (aa)-[:E {role:'subject'}]->(s:N),
      (aa)-[:E {role:'value'}]->(v:N {kind:'Literal'})
RETURN s.text AS subject_iri, v.text AS label, v.lang AS lang
```

Neighborhood of a node (for rendering or inspection):

```cypher
MATCH (seed:N {iri: $iri})-[:E*0..2]-(x:N)
RETURN DISTINCT x.uid AS uid, x.kind AS kind, x.iri AS iri
```

Existential restrictions on a class:

```cypher
MATCH (c:N {iri: $iri})<-[:E {role:'sub'}]-(:N {kind:'SubClassOf'})
      -[:E {role:'super'}]->(r:N {kind:'ObjectSomeValuesFrom'}),
      (r)-[:E {role:'property'}]->(p:N),
      (r)-[:E {role:'filler'}]->(f:N)
RETURN p.iri AS property, f.iri AS filler
```

## Load the whole graph back into Python

```python
graph = proj.graph()          # Graph(nodes, edges)
counts = proj.node_count, proj.edge_count
```
