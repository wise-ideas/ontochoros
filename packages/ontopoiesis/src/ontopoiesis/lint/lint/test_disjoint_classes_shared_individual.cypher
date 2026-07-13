// Individuals directly asserted into two disjoint named classes. This is a direct
// ABox contradiction that does not require a classifier to derive.
MATCH
  (dc:N {kind: 'DisjointClasses'})-[:E {role: 'operand'}]->(a:N {kind: 'Class'}),
  (dc)-[:E {role: 'operand'}]->(b:N {kind: 'Class'}),
  (ax1:N {kind: 'ClassAssertion'})-[:E {role: 'class'}]->(a),
  (ax1)-[:E {role: 'individual'}]->(i:N {kind: 'NamedIndividual'}),
  (ax2:N {kind: 'ClassAssertion'})-[:E {role: 'class'}]->(b),
  (ax2)-[:E {role: 'individual'}]->(i)
WHERE a.iri < b.iri
RETURN
  a.iri AS disjoint_a,
  b.iri AS disjoint_b,
  i.iri AS individual_iri
ORDER BY disjoint_a, disjoint_b, individual_iri
