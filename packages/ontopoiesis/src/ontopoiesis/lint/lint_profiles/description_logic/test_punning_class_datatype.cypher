// IRI used simultaneously as a Class and a Datatype. Classes inhabit the object
// domain; datatypes inhabit the data domain. These roles are disjoint in OWL 2
// semantics, so an IRI spanning both is almost always a namespace collision or
// copy-paste error and cannot be used coherently in either context.
MATCH
    (c:N {kind: 'Class'}),
    (d:N {kind: 'Datatype'})
WHERE c.iri = d.iri
RETURN c.iri AS iri
ORDER BY iri
