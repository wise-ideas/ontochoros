// Example project policy: negative object property assertions are not allowed.
MATCH (ax:N {kind: 'NegativeObjectPropertyAssertion'})
      -[:E {role: 'subject'}]->(source:N)
MATCH (ax)-[:E {role: 'property'}]->(prop:N)
MATCH (ax)-[:E {role: 'object'}]->(target:N)
RETURN
    source.iri AS source,
    prop.iri AS property,
    target.iri AS target
ORDER BY source.iri, prop.iri, target.iri
