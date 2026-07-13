// A named class appearing more than once in the same ObjectIntersectionOf.
// The duplicate member is redundant and signals a copy-paste error or a merge
// gone wrong. Produces one row per (intersection, class) pair with duplicates.
//
// This pattern requires traversing blank-node list structure in SPARQL and
// detecting duplicates across list positions — there is no clean equivalent.
// ROBOT verify has no built-in check for this; a SPARQL approximation requires
// nested sub-selects over reified list triples and is fragile across serialisers.
MATCH
  (i:N {kind: 'ObjectIntersectionOf'})-[e1:E {role: 'operand'}]->(c:N),
  (i)-[e2:E {role: 'operand'}]->(c)
WHERE e1.position < e2.position
RETURN i.uid AS intersection_uid, c.iri AS duplicate_class
