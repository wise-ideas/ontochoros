// Multiple rdfs:label annotations in the same language on the same entity. Values may
// be identical or different. OWL allows this, but consumers that select one display
// label per language need an explicit selection policy.
MATCH
  (ax:N {kind: 'AnnotationAssertion'})
    -[:E {role: 'property'}]->(:N {iri: 'http://www.w3.org/2000/01/rdf-schema#label'}),
  (ax)-[:E {role: 'subject'}]->(subj:N {kind: 'IRI'}),
  (ax)-[:E {role: 'value'}]->(v:N {kind: 'Literal'})
WITH subj.text AS entity_iri, coalesce(v.lang, '') AS language_tag, count(ax) AS label_count
WHERE label_count > 1
RETURN entity_iri, language_tag, label_count
ORDER BY entity_iri, language_tag
