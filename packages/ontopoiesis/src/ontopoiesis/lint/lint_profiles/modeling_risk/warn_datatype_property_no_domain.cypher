// Data properties with no DataPropertyDomain axiom. Without a declared domain,
// the property can be asserted on any individual regardless of type, and reasoners
// cannot infer class membership from its usage. Parallel to the domain side of
// warn_object_property_no_domain_or_range.
MATCH (p:N {kind: 'DataProperty'})
WHERE p.iri IS NOT NULL
  AND NOT p.iri STARTS WITH 'http://www.w3.org/2002/07/owl#'
  AND NOT EXISTS {
    MATCH (:N {kind: 'DataPropertyDomain'})-[:E {role: 'property'}]->(p)
  }
RETURN p.iri AS iri
ORDER BY iri
