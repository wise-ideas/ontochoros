// Individual pairs declared both SameIndividual and DifferentIndividuals.
// Direct contradiction regardless of the open- or closed-world assumption.
MATCH
  (si:N {kind: 'SameIndividual'})-[:E {role: 'operand'}]->(a:N {kind: 'NamedIndividual'}),
  (si)-[:E {role: 'operand'}]->(b:N {kind: 'NamedIndividual'}),
  (di:N {kind: 'DifferentIndividuals'})-[:E {role: 'operand'}]->(a),
  (di)-[:E {role: 'operand'}]->(b)
WHERE a.iri < b.iri
RETURN
  a.iri AS individual_a,
  b.iri AS individual_b
ORDER BY individual_a, individual_b
