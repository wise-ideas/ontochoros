// Entities whose IRI is identical to the ontology IRI itself. This is often confusing
// in published vocabularies, but some projects do it intentionally, so keep it out of
// the default universal baseline.
MATCH (ont:N {kind: 'Ontology'}), (e:N)
WHERE ont.ontology_iri IS NOT NULL
  AND e.iri = ont.ontology_iri
  AND e.kind IN [
    'Class',
    'ObjectProperty',
    'DataProperty',
    'AnnotationProperty',
    'NamedIndividual',
    'Datatype'
  ]
RETURN e.kind AS kind, e.iri AS iri
ORDER BY kind, iri
