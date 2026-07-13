// Literal assertions that violate a DisjointDataProperties axiom by asserting the
// same subject/literal pair through two disjoint data properties. Literals compare
// by structure (text, language, datatype), not projection node identity.
MATCH
  (dp:N {kind: 'DisjointDataProperties'})-[:E {role: 'operand'}]->(p:N {kind: 'DataProperty'}),
  (dp)-[:E {role: 'operand'}]->(q:N {kind: 'DataProperty'}),
  (ax1:N {kind: 'DataPropertyAssertion'})-[:E {role: 'property'}]->(p),
  (ax1)-[:E {role: 'subject'}]->(src:N {kind: 'NamedIndividual'}),
  (ax1)-[:E {role: 'object'}]->(v1:N {kind: 'Literal'}),
  (ax2:N {kind: 'DataPropertyAssertion'})-[:E {role: 'property'}]->(q),
  (ax2)-[:E {role: 'subject'}]->(src),
  (ax2)-[:E {role: 'object'}]->(v2:N {kind: 'Literal'})
WHERE p.iri < q.iri
  AND v1.text = v2.text
  AND coalesce(v1.lang, '') = coalesce(v2.lang, '')
  AND coalesce(v1.datatype_iri, '') = coalesce(v2.datatype_iri, '')
RETURN
  p.iri AS property_a_iri,
  q.iri AS property_b_iri,
  src.iri AS source_iri,
  v1.text
    + CASE WHEN v1.lang IS NULL THEN '' ELSE '@' + v1.lang END
    + CASE WHEN v1.datatype_iri IS NULL THEN '' ELSE '^^' + v1.datatype_iri END AS target_literal
ORDER BY property_a_iri, property_b_iri, source_iri, target_literal
