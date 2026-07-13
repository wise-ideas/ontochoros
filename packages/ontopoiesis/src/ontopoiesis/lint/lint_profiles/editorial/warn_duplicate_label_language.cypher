// Multiple rdfs:label annotations in the same language on the same entity. OWL allows
// this, but applications can only display one label per language, and the choice is
// arbitrary. In practice this almost always indicates a copy-paste duplicate or an
// accidental re-assertion after an edit.
MATCH
  (ax:N {kind: 'AnnotationAssertion'})
    -[:E {role: 'property'}]->(:N {iri: 'http://www.w3.org/2000/01/rdf-schema#label'}),
  (ax)-[:E {role: 'subject'}]->(subj:N {kind: 'IRI'}),
  (ax)-[:E {role: 'value'}]->(v:N {kind: 'Literal'})
WITH subj.text AS entity_iri, coalesce(v.lang, '') AS language_tag, count(ax) AS label_count
WHERE label_count > 1
RETURN entity_iri, language_tag, label_count
ORDER BY entity_iri, language_tag
