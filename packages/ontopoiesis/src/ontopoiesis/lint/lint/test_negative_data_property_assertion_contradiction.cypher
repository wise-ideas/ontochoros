// DataPropertyAssertion(P, a, v) and NegativeDataPropertyAssertion(P, a, v) both exist
// for the same property, source individual, and literal term. This compares literal
// structure rather than projection node identity so duplicate literal nodes with the
// same value are still detected.
MATCH
  (pos:N {kind: 'DataPropertyAssertion'})-[:E {role: 'property'}]->(p:N {kind: 'DataProperty'}),
  (pos)-[:E {role: 'subject'}]->(src:N {kind: 'NamedIndividual'}),
  (pos)-[:E {role: 'object'}]->(pos_val:N {kind: 'Literal'}),
  (neg:N {kind: 'NegativeDataPropertyAssertion'})-[:E {role: 'property'}]->(p),
  (neg)-[:E {role: 'subject'}]->(src),
  (neg)-[:E {role: 'object'}]->(neg_val:N {kind: 'Literal'})
WHERE pos_val.text = neg_val.text
  AND coalesce(pos_val.lang, '') = coalesce(neg_val.lang, '')
  AND coalesce(pos_val.datatype_iri, '') = coalesce(neg_val.datatype_iri, '')
RETURN
  p.iri AS property_iri,
  src.iri AS source_iri,
  pos_val.text
    + CASE WHEN pos_val.lang IS NULL THEN '' ELSE '@' + pos_val.lang END
    + CASE WHEN pos_val.datatype_iri IS NULL THEN '' ELSE '^^' + pos_val.datatype_iri END AS target_literal
ORDER BY property_iri, source_iri, target_literal
