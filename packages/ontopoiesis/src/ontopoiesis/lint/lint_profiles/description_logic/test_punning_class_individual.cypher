// IRI used simultaneously as a Class and a NamedIndividual. OWL 2 permits punning
// in limited contexts, but Class/Individual punning almost always results from a
// copy-paste error or from conflating the taxonomy with instance data, and causes
// reasoning anomalies when the same IRI is interpreted as both a concept and an instance.
MATCH
    (c:N {kind: 'Class'}),
    (i:N {kind: 'NamedIndividual'})
WHERE c.iri = i.iri
RETURN c.iri AS iri
ORDER BY iri
