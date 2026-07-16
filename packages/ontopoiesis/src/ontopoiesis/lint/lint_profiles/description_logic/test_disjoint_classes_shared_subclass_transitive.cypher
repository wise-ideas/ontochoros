// A class that is a subclass — at ANY depth — of two classes declared disjoint is
// unsatisfiable (equivalent to owl:Nothing): it inherits from two provably disjoint
// parents. This generalizes the direct check E103 through the derived subclass_of closure,
// catching deep unsatisfiabilities that a reasoner would flag but a one-hop structural
// check misses. It is anchored on the (few) disjoint pairs and then walks descendants, so
// it stays tractable; depth is capped at 20. Kept in the opt-in description_logic profile
// because the closure walk is heavier than the default baseline checks. It subsumes E103,
// so the direct cases also appear here when both are run.
MATCH (a:N)-[:D {relation: 'disjoint_class'}]->(b:N)
WHERE a.iri < b.iri
MATCH (c:N)-[:D*1..20 {relation:'subclass_of'}]->(a),
      (c)-[:D*1..20 {relation:'subclass_of'}]->(b)
RETURN DISTINCT c.iri AS unsatisfiable_class, a.iri AS disjoint_a, b.iri AS disjoint_b
UNION
// Degenerate case: a disjoint class that is itself a subclass (at any depth) of the class
// it is disjoint with. The branch above needs a path of length >= 1 to BOTH parents, so
// c = a never matches there. Both directions of disjoint_class are materialized, so this
// single directed pattern catches a below b and b below a alike.
MATCH (a:N)-[:D {relation: 'disjoint_class'}]->(b:N)
MATCH (a)-[:D*1..20 {relation:'subclass_of'}]->(b)
RETURN DISTINCT a.iri AS unsatisfiable_class,
       CASE WHEN a.iri < b.iri THEN a.iri ELSE b.iri END AS disjoint_a,
       CASE WHEN a.iri < b.iri THEN b.iri ELSE a.iri END AS disjoint_b
ORDER BY unsatisfiable_class, disjoint_a, disjoint_b
