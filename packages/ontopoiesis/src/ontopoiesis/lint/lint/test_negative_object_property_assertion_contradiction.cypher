// ObjectPropertyAssertion(P, a, b) and NegativeObjectPropertyAssertion(P, a, b) both
// exist for the same property, source, and target. A negative property assertion
// explicitly states the triple does NOT hold, so affirming it simultaneously is a direct
// contradiction regardless of the open- or closed-world assumption.
MATCH
  (pos:N {kind: 'ObjectPropertyAssertion'})-[:E {role: 'property'}]->(p:N {kind: 'ObjectProperty'}),
  (pos)-[:E {role: 'subject'}]->(src:N {kind: 'NamedIndividual'}),
  (pos)-[:E {role: 'object'}]->(tgt:N {kind: 'NamedIndividual'}),
  (neg:N {kind: 'NegativeObjectPropertyAssertion'})-[:E {role: 'property'}]->(p),
  (neg)-[:E {role: 'subject'}]->(src),
  (neg)-[:E {role: 'object'}]->(tgt)
RETURN
  p.iri AS property_iri,
  src.iri AS source_iri,
  tgt.iri AS target_iri
ORDER BY property_iri, source_iri, target_iri
