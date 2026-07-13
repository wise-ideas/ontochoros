// Entities marked owl:deprecated that still appear in structural axioms or class
// expressions. Excludes the entity's own Declaration (which is expected to remain).
// This is useful migration guidance, but not a universal logical contradiction, so it
// lives in the editorial profile rather than the default baseline.
MATCH (e:N)
WHERE
  e.kind IN [
    'Class',
    'ObjectProperty',
    'DataProperty',
    'AnnotationProperty',
    'NamedIndividual'
  ]
  AND e.iri IS NOT NULL
  AND NOT e.iri STARTS WITH 'http://www.w3.org/2002/07/owl#'
  AND EXISTS {
    MATCH
      (dep:N {kind: 'AnnotationAssertion'})
        -[:E {role: 'property'}]->(:N {iri: 'http://www.w3.org/2002/07/owl#deprecated'}),
      (dep)-[:E {role: 'subject'}]->(subj:N {kind: 'IRI'})
    WHERE subj.text = e.iri
  }
  AND EXISTS {
    MATCH (ref:N)-[:E]->(e)
    WHERE ref.kind <> 'Declaration'
  }
RETURN e.kind AS kind, e.iri AS iri
ORDER BY kind, iri
