// IRI used simultaneously as a DataProperty and an AnnotationProperty.
// OWL 2 DL explicitly permits this (annotation punning), but range constraints
// and typing rules declared against the data property role are not enforced when
// the same IRI is accessed through annotation traversal.
MATCH
    (d:N {kind: 'DataProperty'}),
    (a:N {kind: 'AnnotationProperty'})
WHERE d.iri = a.iri
RETURN d.iri AS iri
ORDER BY iri
