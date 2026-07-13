// Assertions that violate an AsymmetricObjectProperty declaration. Asymmetry means
// if P(a, b) holds then P(b, a) must not hold, and it also rules out self-loops
// because P(a, a) would imply its own converse.
MATCH (:N {kind: 'AsymmetricObjectProperty'})-[:E {role: 'property'}]->(p:N {kind: 'ObjectProperty'})
WHERE p.iri IS NOT NULL
MATCH
  (ax:N {kind: 'ObjectPropertyAssertion'})-[:E {role: 'property'}]->(p),
  (ax)-[:E {role: 'subject'}]->(a:N {kind: 'NamedIndividual'}),
  (ax)-[:E {role: 'object'}]->(b:N {kind: 'NamedIndividual'})
WHERE
  a = b
  OR (
    a.iri < b.iri
    AND EXISTS {
      MATCH
        (reverse:N {kind: 'ObjectPropertyAssertion'})-[:E {role: 'property'}]->(p),
        (reverse)-[:E {role: 'subject'}]->(b),
        (reverse)-[:E {role: 'object'}]->(a)
    }
  )
RETURN DISTINCT
  p.iri AS property_iri,
  a.iri AS individual_a,
  b.iri AS individual_b
ORDER BY property_iri, individual_a, individual_b
