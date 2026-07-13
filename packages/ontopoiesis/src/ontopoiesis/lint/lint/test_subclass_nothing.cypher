// Classes with an explicit SubClassOf to owl:Nothing, asserting unsatisfiability
// directly in the axiom set without requiring a reasoner to derive it.
MATCH
  (ax:N {kind: 'SubClassOf'})-[:E {role: 'sub'}]->(c:N {kind: 'Class'}),
  (ax)-[:E {role: 'super'}]->(:N {iri: 'http://www.w3.org/2002/07/owl#Nothing'})
WHERE c.iri IS NOT NULL
  AND NOT c.iri STARTS WITH 'http://www.w3.org/2002/07/owl#'
RETURN c.iri AS iri
ORDER BY iri
