// Object property assertions that violate an IrreflexiveObjectProperty declaration by
// relating an individual to itself.
MATCH (:N {kind: 'IrreflexiveObjectProperty'})-[:E {role: 'property'}]->(p:N {kind: 'ObjectProperty'})
WHERE p.iri IS NOT NULL
MATCH
  (ax:N {kind: 'ObjectPropertyAssertion'})-[:E {role: 'property'}]->(p),
  (ax)-[:E {role: 'subject'}]->(i:N {kind: 'NamedIndividual'}),
  (ax)-[:E {role: 'object'}]->(i)
RETURN
  p.iri AS property_iri,
  i.iri AS individual_iri
ORDER BY property_iri, individual_iri
