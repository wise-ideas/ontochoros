// Named entities with no rdfs:label. Without labels, entities are identified only by
// IRI in every human-facing tool, making the ontology unusable for most applications.
// Warning rather than error because a label-free ontology is structurally valid OWL;
// when imports are loaded, this fires for imported terms whose labels live elsewhere.
MATCH (e:N)
WHERE
  e.kind IN [
    'Class',
    'ObjectProperty',
    'DataProperty',
    'AnnotationProperty',
    'NamedIndividual',
    'Datatype'
  ]
  AND e.iri IS NOT NULL
  AND NOT e.iri STARTS WITH 'http://www.w3.org/2002/07/owl#'
  AND NOT e.iri STARTS WITH 'http://www.w3.org/2000/01/rdf-schema#'
  AND NOT e.iri STARTS WITH 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  AND NOT e.iri STARTS WITH 'http://www.w3.org/2001/XMLSchema#'
  AND NOT EXISTS {
    MATCH
      (ax:N {kind: 'AnnotationAssertion'})
        -[:E {role: 'property'}]->(:N {iri: 'http://www.w3.org/2000/01/rdf-schema#label'}),
      (ax)-[:E {role: 'subject'}]->(subj:N {kind: 'IRI'})
    WHERE subj.text = e.iri
  }
RETURN
  e.kind AS kind,
  e.iri AS iri
ORDER BY kind, iri
