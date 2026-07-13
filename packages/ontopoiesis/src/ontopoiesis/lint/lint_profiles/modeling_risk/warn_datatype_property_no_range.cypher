// Data properties with no DataPropertyRange axiom. Without a declared range the
// property accepts any literal value, which usually indicates an incomplete schema.
// Parallel to warn_object_property_no_domain_or_range for object properties.
MATCH (p:N {kind: 'DataProperty'})
WHERE p.iri IS NOT NULL
  AND NOT p.iri STARTS WITH 'http://www.w3.org/2002/07/owl#'
  AND NOT EXISTS {
    MATCH (:N {kind: 'DataPropertyRange'})-[:E {role: 'property'}]->(p)
  }
RETURN p.iri AS iri
ORDER BY iri
