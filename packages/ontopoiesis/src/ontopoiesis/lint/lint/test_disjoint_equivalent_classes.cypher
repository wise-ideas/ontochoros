// Class pairs that appear together in both an EquivalentClasses and a DisjointClasses
// axiom. This directly implies both classes are unsatisfiable (equivalent to owl:Nothing).
// Distinct from test_disjoint_classes_shared_subclass, which requires a third witness class.
MATCH
  (ec:N {kind: 'EquivalentClasses'})-[:E {role: 'operand'}]->(a:N {kind: 'Class'}),
  (ec)-[:E {role: 'operand'}]->(b:N {kind: 'Class'}),
  (dc:N {kind: 'DisjointClasses'})-[:E {role: 'operand'}]->(a),
  (dc)-[:E {role: 'operand'}]->(b)
WHERE a.iri < b.iri
RETURN
  a.iri AS class_a,
  b.iri AS class_b
ORDER BY class_a, class_b
