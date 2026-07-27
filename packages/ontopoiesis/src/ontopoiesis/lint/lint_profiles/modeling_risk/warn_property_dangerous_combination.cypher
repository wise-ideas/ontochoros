// Object properties with characteristic combinations that produce strong and often
// unintended consequences under reasoning:
//   Transitive + Functional: collapses the entire forward chain to a single target value.
//   Transitive + InverseFunctional: collapses the entire backward chain to a single source.
//   Functional + InverseFunctional: makes the asserted relation one-to-one among
//   participating individuals; it does not require every domain/range individual to
//   participate.
MATCH (p:N {kind: 'ObjectProperty'})
WHERE p.iri IS NOT NULL
  AND EXISTS {
    MATCH (:N {kind: 'TransitiveObjectProperty'})-[:E {role: 'property'}]->(p)
  }
  AND EXISTS {
    MATCH (:N {kind: 'FunctionalObjectProperty'})-[:E {role: 'property'}]->(p)
  }
RETURN p.iri AS property_iri, 'transitive_and_functional' AS combination

UNION ALL

MATCH (p:N {kind: 'ObjectProperty'})
WHERE p.iri IS NOT NULL
  AND EXISTS {
    MATCH (:N {kind: 'TransitiveObjectProperty'})-[:E {role: 'property'}]->(p)
  }
  AND EXISTS {
    MATCH (:N {kind: 'InverseFunctionalObjectProperty'})-[:E {role: 'property'}]->(p)
  }
RETURN p.iri AS property_iri, 'transitive_and_inverse_functional' AS combination

UNION ALL

MATCH (p:N {kind: 'ObjectProperty'})
WHERE p.iri IS NOT NULL
  AND EXISTS {
    MATCH (:N {kind: 'FunctionalObjectProperty'})-[:E {role: 'property'}]->(p)
  }
  AND EXISTS {
    MATCH (:N {kind: 'InverseFunctionalObjectProperty'})-[:E {role: 'property'}]->(p)
  }
RETURN p.iri AS property_iri, 'functional_and_inverse_functional' AS combination

ORDER BY property_iri, combination
