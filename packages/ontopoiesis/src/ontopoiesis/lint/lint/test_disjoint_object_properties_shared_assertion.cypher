// Object property assertions that violate a DisjointObjectProperties axiom by
// asserting the same subject/target pair through two disjoint object properties.
MATCH
  (dp:N {kind: 'DisjointObjectProperties'})-[:E {role: 'operand'}]->(p:N {kind: 'ObjectProperty'}),
  (dp)-[:E {role: 'operand'}]->(q:N {kind: 'ObjectProperty'}),
  (ax1:N {kind: 'ObjectPropertyAssertion'})-[:E {role: 'property'}]->(p),
  (ax1)-[:E {role: 'subject'}]->(src:N {kind: 'NamedIndividual'}),
  (ax1)-[:E {role: 'object'}]->(tgt:N {kind: 'NamedIndividual'}),
  (ax2:N {kind: 'ObjectPropertyAssertion'})-[:E {role: 'property'}]->(q),
  (ax2)-[:E {role: 'subject'}]->(src),
  (ax2)-[:E {role: 'object'}]->(tgt)
WHERE p.iri < q.iri
RETURN
  p.iri AS property_a_iri,
  q.iri AS property_b_iri,
  src.iri AS source_iri,
  tgt.iri AS target_iri
ORDER BY property_a_iri, property_b_iri, source_iri, target_iri
