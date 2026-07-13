// Functional object properties where the same source individual has two distinct named
// target individuals. Under the Unique Name Assumption this is an inconsistency; without
// it a reasoner will silently merge the targets, which is almost always unintended.
MATCH (:N {kind: 'FunctionalObjectProperty'})-[:E {role: 'property'}]->(p:N {kind: 'ObjectProperty'})
WHERE p.iri IS NOT NULL
MATCH
  (ax1:N {kind: 'ObjectPropertyAssertion'})-[:E {role: 'property'}]->(p),
  (ax1)-[:E {role: 'subject'}]->(src:N {kind: 'NamedIndividual'}),
  (ax1)-[:E {role: 'object'}]->(t1:N {kind: 'NamedIndividual'}),
  (ax2:N {kind: 'ObjectPropertyAssertion'})-[:E {role: 'property'}]->(p),
  (ax2)-[:E {role: 'subject'}]->(src),
  (ax2)-[:E {role: 'object'}]->(t2:N {kind: 'NamedIndividual'})
WHERE ax1.uid < ax2.uid
  AND t1.iri <> t2.iri
  AND NOT EXISTS {
    MATCH
      (si:N {kind: 'SameIndividual'})-[:E {role: 'operand'}]->(t1),
      (si)-[:E {role: 'operand'}]->(t2)
  }
RETURN
  p.iri AS property_iri,
  src.iri AS source_individual_iri,
  t1.iri AS target_1_iri,
  t2.iri AS target_2_iri
ORDER BY property_iri, source_individual_iri, target_1_iri, target_2_iri
