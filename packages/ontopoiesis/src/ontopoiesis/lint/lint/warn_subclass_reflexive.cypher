// A class asserted to be a subclass of itself (A ⊑ A). Every class is trivially a
// subclass of itself, so this is redundant rather than inconsistent; it usually comes
// from editor round-trips or accidental copy/paste. Fires on the derived subclass_of
// self-loop, which comes from an asserted SubClassOf(C, C) or — deliberately — from a
// DisjointUnion that lists the union class among its own operands (the same authoring
// accident wearing a different axiom).
MATCH (c:N)-[:D {relation: 'subclass_of'}]->(c)
RETURN c.iri AS iri
ORDER BY iri
