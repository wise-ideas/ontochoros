// 2-node subclass cycles: A ⊑ B and B ⊑ A both asserted. This is legal OWL and simply
// makes the classes equivalent, but it is often an accidental normalization problem.
// Keep it as a modeling-risk warning rather than a baseline failure.
MATCH
  (a:N {kind: 'Class'})<-[:E {role: 'sub'}]
    -(:N {kind: 'SubClassOf'})
    -[:E {role: 'super'}]->(b:N {kind: 'Class'}),
  (b)<-[:E {role: 'sub'}]
    -(:N {kind: 'SubClassOf'})
    -[:E {role: 'super'}]->(a)
WHERE a.iri < b.iri
RETURN
  a.iri AS class_a,
  b.iri AS class_b
ORDER BY class_a, class_b
