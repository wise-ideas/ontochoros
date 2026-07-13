// 3-node subclass cycles: A ⊑ B ⊑ C ⊑ A. This is legal OWL and collapses the classes
// into one equivalence set, but it is usually a hierarchy-maintenance smell.
// 2-node cycles are caught by warn_subclass_cycle_direct.cypher.
MATCH
  (a:N {kind: 'Class'})<-[:E {role: 'sub'}]
    -(:N {kind: 'SubClassOf'})
    -[:E {role: 'super'}]->(b:N {kind: 'Class'}),
  (b)<-[:E {role: 'sub'}]
    -(:N {kind: 'SubClassOf'})
    -[:E {role: 'super'}]->(c:N {kind: 'Class'}),
  (c)<-[:E {role: 'sub'}]
    -(:N {kind: 'SubClassOf'})
    -[:E {role: 'super'}]->(a)
WHERE a.iri < b.iri AND a.iri < c.iri
  AND b.iri < c.iri
RETURN
  a.iri AS class_a,
  b.iri AS class_b,
  c.iri AS class_c

UNION

MATCH
  (a:N {kind: 'Class'})<-[:E {role: 'sub'}]
    -(:N {kind: 'SubClassOf'})
    -[:E {role: 'super'}]->(c:N {kind: 'Class'}),
  (c)<-[:E {role: 'sub'}]
    -(:N {kind: 'SubClassOf'})
    -[:E {role: 'super'}]->(b:N {kind: 'Class'}),
  (b)<-[:E {role: 'sub'}]
    -(:N {kind: 'SubClassOf'})
    -[:E {role: 'super'}]->(a)
WHERE a.iri < b.iri AND a.iri < c.iri
  AND b.iri < c.iri
RETURN
  a.iri AS class_a,
  b.iri AS class_b,
  c.iri AS class_c
ORDER BY class_a, class_b, class_c
