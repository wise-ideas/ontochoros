// Named individuals with no ClassAssertion — present in the signature but untyped.
// Under the open-world assumption this is not an error, but it commonly indicates
// an incomplete ABox or an individual that was declared and then forgotten.
MATCH (i:N {kind: 'NamedIndividual'})
WHERE i.iri IS NOT NULL
  AND NOT EXISTS {
    MATCH (:N {kind: 'ClassAssertion'})-[:E {role: 'individual'}]->(i)
  }
RETURN i.iri AS iri
ORDER BY iri
