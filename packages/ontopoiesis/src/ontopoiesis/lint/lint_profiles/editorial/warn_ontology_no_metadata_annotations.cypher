// Ontology has no common metadata annotations such as title, creator, description, or
// license. Metadata annotations are essential for provenance and discovery.
MATCH (ont:N {kind: 'Ontology'})
WHERE ont.ontology_iri IS NOT NULL
  AND NOT EXISTS {
    MATCH
      (ont)-[:E {role: 'annotation'}]->(ann:N {kind: 'Annotation'}),
      (ann)-[:E {role: 'property'}]->(prop:N {kind: 'AnnotationProperty'})
    WHERE prop.iri IN [
      'http://purl.org/dc/elements/1.1/title',
      'http://purl.org/dc/elements/1.1/creator',
      'http://purl.org/dc/elements/1.1/description',
      'http://purl.org/dc/elements/1.1/license',
      'http://purl.org/dc/terms/title',
      'http://purl.org/dc/terms/creator',
      'http://purl.org/dc/terms/description',
      'http://purl.org/dc/terms/license'
    ]
  }
RETURN ont.ontology_iri AS ontology_iri
