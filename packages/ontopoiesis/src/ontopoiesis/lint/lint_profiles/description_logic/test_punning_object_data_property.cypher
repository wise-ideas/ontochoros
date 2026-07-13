// IRI used simultaneously as an ObjectProperty and a DataProperty. Object properties
// relate individuals to individuals; data properties relate individuals to literals.
// These roles are disjoint in OWL 2 — a single IRI cannot serve both, and any axiom
// using it will be interpreted under one role only, silently ignoring the other.
MATCH
    (o:N {kind: 'ObjectProperty'}),
    (d:N {kind: 'DataProperty'})
WHERE o.iri = d.iri
RETURN o.iri AS iri
ORDER BY iri
