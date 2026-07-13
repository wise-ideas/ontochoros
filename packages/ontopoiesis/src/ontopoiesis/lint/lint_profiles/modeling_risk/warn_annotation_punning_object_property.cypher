// IRI used simultaneously as an ObjectProperty and an AnnotationProperty.
// OWL 2 DL explicitly permits this (annotation punning), but the overlap creates
// a semantic gap: axioms written against the object property role are invisible
// to tools that traverse the same IRI as an annotation property, and vice versa.
MATCH
    (o:N {kind: 'ObjectProperty'}),
    (a:N {kind: 'AnnotationProperty'})
WHERE o.iri = a.iri
RETURN o.iri AS iri
ORDER BY iri
