// The same SubClassOf(A, B) pair stated by more than one axiom. Report each repeated
// pair once rather than once per duplicate-axiom combination.
MATCH
  (ax:N {kind: 'SubClassOf'})-[:E {role: 'sub'}]->(sub:N {kind: 'Class'}),
  (ax)-[:E {role: 'super'}]->(sup:N {kind: 'Class'})
WITH sub, sup, count(*) AS axiom_count
WHERE axiom_count > 1
RETURN
  sub.iri AS sub_class,
  sup.iri AS super_class
ORDER BY sub_class, super_class
