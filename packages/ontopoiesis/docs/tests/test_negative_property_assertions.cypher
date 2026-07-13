// Example project policy: negative object property assertions are not allowed.
MATCH (ax:N {kind: 'NegativeObjectPropertyAssertion'})
      -[:E {role: 'source_individual'}]->(source:N)
MATCH (ax)-[:E {role: 'object_property_expression'}]->(prop:N)
MATCH (ax)-[:E {role: 'target_individual'}]->(target:N)
RETURN
    source.iri AS source,
    prop.iri AS property,
    target.iri AS target
ORDER BY source.iri, prop.iri, target.iri
