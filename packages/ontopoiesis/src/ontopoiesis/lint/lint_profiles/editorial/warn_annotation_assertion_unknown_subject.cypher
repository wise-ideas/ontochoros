// AnnotationAssertion axioms whose subject IRI does not appear anywhere else in the
// ontology graph as either an entity IRI or the ontology IRI. This is intentionally
// weaker than "missing Declaration": OWL 2 allows undeclared entities, so the warning
// should focus on genuinely dangling annotation subjects rather than profile style.
// Only full-IRI subjects are checked: anonymous-individual subjects are always local,
// and abbreviated-IRI subjects would need prefix expansion to compare.
MATCH (ax:N {kind: 'AnnotationAssertion'})-[:E {role: 'subject'}]->(subj:N {kind: 'IRI'})
WHERE subj.text IS NOT NULL
  AND NOT subj.text STARTS WITH 'http://www.w3.org/2002/07/owl#'
  AND NOT subj.text STARTS WITH 'http://www.w3.org/2000/01/rdf-schema#'
  AND NOT subj.text STARTS WITH 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  AND NOT subj.text STARTS WITH 'http://www.w3.org/2001/XMLSchema#'
  AND NOT EXISTS {
    MATCH (n:N)
    WHERE n.iri = subj.text OR n.ontology_iri = subj.text
  }
RETURN DISTINCT subj.text AS subject_iri
ORDER BY subject_iri
