// Object property assertions against owl:bottomObjectProperty. The bottom object
// property is defined to have no extension, so any explicit assertion using it is
// impossible.
MATCH
  (ax:N {kind: 'ObjectPropertyAssertion'})
    -[:E {role: 'property'}]->(:N {iri: 'http://www.w3.org/2002/07/owl#bottomObjectProperty'}),
  (ax)-[:E {role: 'subject'}]->(src:N {kind: 'NamedIndividual'}),
  (ax)-[:E {role: 'object'}]->(tgt:N {kind: 'NamedIndividual'})
RETURN
  src.iri AS source_iri,
  tgt.iri AS target_iri
ORDER BY source_iri, target_iri
