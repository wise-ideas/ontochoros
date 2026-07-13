// A class that is a direct SubClassOf two classes declared DisjointClasses. The shared
// subclass must be unsatisfiable (equivalent to owl:Nothing): it simultaneously inherits
// from two disjoint parents. Detectable from the axiom structure alone — no classifier
// run required — making it a useful pre-reasoning consistency check.
MATCH
  (dc:N {kind: 'DisjointClasses'})-[:E {role: 'operand'}]->(a:N {kind: 'Class'}),
  (dc)-[:E {role: 'operand'}]->(b:N {kind: 'Class'}),
  (ax1:N {kind: 'SubClassOf'})-[:E {role: 'sub'}]->(c:N {kind: 'Class'}),
  (ax1)-[:E {role: 'super'}]->(a),
  (ax2:N {kind: 'SubClassOf'})-[:E {role: 'sub'}]->(c),
  (ax2)-[:E {role: 'super'}]->(b)
WHERE a.iri < b.iri
RETURN
  a.iri AS disjoint_a,
  b.iri AS disjoint_b,
  c.iri AS shared_subclass
ORDER BY disjoint_a, disjoint_b, shared_subclass
