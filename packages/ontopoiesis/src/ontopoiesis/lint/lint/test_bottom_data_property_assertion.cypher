// Data property assertions against owl:bottomDataProperty. The bottom data property
// is defined to have no extension, so any explicit assertion using it is impossible.
MATCH
  (ax:N {kind: 'DataPropertyAssertion'})
    -[:E {role: 'property'}]->(:N {iri: 'http://www.w3.org/2002/07/owl#bottomDataProperty'}),
  (ax)-[:E {role: 'subject'}]->(src:N {kind: 'NamedIndividual'}),
  (ax)-[:E {role: 'object'}]->(value:N {kind: 'Literal'})
RETURN
  src.iri AS source_iri,
  value.text
    + CASE WHEN value.lang IS NULL THEN '' ELSE '@' + value.lang END
    + CASE WHEN value.datatype_iri IS NULL THEN '' ELSE '^^' + value.datatype_iri END AS target_literal
ORDER BY source_iri, target_literal
