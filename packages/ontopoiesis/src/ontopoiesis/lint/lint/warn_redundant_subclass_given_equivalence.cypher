// SubClassOf(A, B) where an EquivalentClasses axiom already covers both A and B,
// making the SubClassOf entailed and redundant. Adds noise to the axiom set without
// adding information; editors and pipelines often create these unintentionally.
MATCH
  (ax:N {kind: 'SubClassOf'})-[:E {role: 'sub'}]->(a:N {kind: 'Class'}),
  (ax)-[:E {role: 'super'}]->(b:N {kind: 'Class'}),
  (ec:N {kind: 'EquivalentClasses'})-[:E {role: 'operand'}]->(a),
  (ec)-[:E {role: 'operand'}]->(b)
WHERE a.iri IS NOT NULL AND b.iri IS NOT NULL
RETURN DISTINCT
  a.iri AS sub_class,
  b.iri AS super_class
ORDER BY sub_class, super_class
