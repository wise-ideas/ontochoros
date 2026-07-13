// Object properties with neither an ObjectPropertyDomain nor an ObjectPropertyRange
// axiom. Without either, the property is unconstrained: reasoners cannot infer class
// membership from its usage, and documentation tools have no structural context to
// display. Properties with only domain or only range declared are not flagged.
MATCH (p:N {kind: 'ObjectProperty'})
WHERE p.iri IS NOT NULL
  AND NOT p.iri STARTS WITH 'http://www.w3.org/2002/07/owl#'
  AND NOT EXISTS {
    MATCH (:N {kind: 'ObjectPropertyDomain'})-[:E {role: 'property'}]->(p)
  }
  AND NOT EXISTS {
    MATCH (:N {kind: 'ObjectPropertyRange'})-[:E {role: 'property'}]->(p)
  }
RETURN p.iri AS iri
ORDER BY iri
