// DisjointUnion(P, A, B, ...) already entails A ⊑ P, B ⊑ P, etc. as part of its
// semantics (it defines P as equivalent to the union of its members). A separate
// SubClassOf(A, P) is therefore redundant and adds noise without adding information.
// Parallel to warn_redundant_subclass_given_equivalence for EquivalentClasses.
MATCH
  (du:N {kind: 'DisjointUnion'})-[:E {role: 'class'}]->(parent:N {kind: 'Class'}),
  (du)-[:E {role: 'operand'}]->(member:N {kind: 'Class'}),
  (ax:N {kind: 'SubClassOf'})-[:E {role: 'sub'}]->(member),
  (ax)-[:E {role: 'super'}]->(parent)
WHERE parent.iri IS NOT NULL AND member.iri IS NOT NULL
RETURN DISTINCT
  parent.iri AS disjoint_union_parent,
  member.iri AS redundant_subclass_member
ORDER BY disjoint_union_parent, redundant_subclass_member
