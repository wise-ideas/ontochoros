// SubClassOf axiom where sub and super are the same class (A ⊑ A). Every class is
// trivially a subclass of itself, so this axiom is redundant rather than inconsistent.
// Keep it as a warning because it usually comes from editor round-trips or accidental
// copy/paste, not from a logical contradiction.
MATCH
  (ax:N {kind: 'SubClassOf'})-[:E {role: 'sub'}]->(c:N {kind: 'Class'}),
  (ax)-[:E {role: 'super'}]->(c)
RETURN c.iri AS iri
ORDER BY iri
