// Ontology has an IRI but no version IRI. Without a version IRI, consumers cannot
// distinguish between revisions of the same ontology.
MATCH (ont:N {kind: 'Ontology'})
WHERE ont.ontology_iri IS NOT NULL
  AND ont.version_iri IS NULL
RETURN ont.ontology_iri AS ontology_iri
