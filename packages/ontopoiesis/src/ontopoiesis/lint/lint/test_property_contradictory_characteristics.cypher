// Object properties declared with mutually contradictory characteristics.
// Reflexive + Irreflexive entails the property has no instances.
// Symmetric + Asymmetric entails the same.
// A reasoner catches these as inconsistencies, but only when the rest of the
// ontology is consistent enough to run.
MATCH (p:N {kind: 'ObjectProperty'})
WHERE p.iri IS NOT NULL
  AND EXISTS {
    MATCH (:N {kind: 'ReflexiveObjectProperty'})-[:E {role: 'property'}]->(p)
  }
  AND EXISTS {
    MATCH (:N {kind: 'IrreflexiveObjectProperty'})-[:E {role: 'property'}]->(p)
  }
RETURN p.iri AS property_iri, 'reflexive_and_irreflexive' AS contradiction

UNION ALL

MATCH (p:N {kind: 'ObjectProperty'})
WHERE p.iri IS NOT NULL
  AND EXISTS {
    MATCH (:N {kind: 'SymmetricObjectProperty'})-[:E {role: 'property'}]->(p)
  }
  AND EXISTS {
    MATCH (:N {kind: 'AsymmetricObjectProperty'})-[:E {role: 'property'}]->(p)
  }
RETURN p.iri AS property_iri, 'symmetric_and_asymmetric' AS contradiction

ORDER BY property_iri, contradiction
