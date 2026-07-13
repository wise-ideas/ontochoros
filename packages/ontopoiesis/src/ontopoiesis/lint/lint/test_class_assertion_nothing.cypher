// Individuals asserted as instances of owl:Nothing via ClassAssertion.
// owl:Nothing has no instances by definition, so this is a direct contradiction.
MATCH
  (ax:N {kind: 'ClassAssertion'})-[:E {role: 'class'}]->(:N {iri: 'http://www.w3.org/2002/07/owl#Nothing'}),
  (ax)-[:E {role: 'individual'}]->(i:N {kind: 'NamedIndividual'})
WHERE i.iri IS NOT NULL
RETURN i.iri AS iri
ORDER BY iri
