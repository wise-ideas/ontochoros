// Named entities that have an rdfs:label but no definition annotation from any of the
// common definition properties: skos:definition, IAO:0000115 (OBO), dc:description,
// dcterms:description. Catches entities that were named but not described.
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
  AND EXISTS {
    MATCH
      (ax:N {kind: 'AnnotationAssertion'})
        -[:E {role: 'property'}]->(:N {iri: 'http://www.w3.org/2000/01/rdf-schema#label'}),
      (ax)-[:E {role: 'subject'}]->(subj:N {kind: 'IRI'})
    WHERE subj.text = e.iri
  }
  AND NOT EXISTS {
    MATCH
      (ax:N {kind: 'AnnotationAssertion'})-[:E {role: 'property'}]->(prop:N),
      (ax)-[:E {role: 'subject'}]->(subj:N {kind: 'IRI'})
    WHERE subj.text = e.iri
      AND prop.iri IN [
        'http://www.w3.org/2004/02/skos/core#definition',
        'http://purl.obolibrary.org/obo/IAO_0000115',
        'http://purl.org/dc/elements/1.1/description',
        'http://purl.org/dc/terms/description'
      ]
  }
RETURN e.kind AS kind, e.iri AS iri
ORDER BY kind, iri
