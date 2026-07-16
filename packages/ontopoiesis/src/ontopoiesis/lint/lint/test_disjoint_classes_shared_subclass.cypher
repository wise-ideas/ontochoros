// A class that is a direct SubClassOf two classes declared DisjointClasses. The shared
// subclass must be unsatisfiable (equivalent to owl:Nothing): it simultaneously inherits
// from two disjoint parents. Detectable from the axiom structure alone — no classifier
// run required — making it a useful pre-reasoning consistency check.
MATCH (c:N)-[:D {relation: 'subclass_of'}]->(a:N),
      (c)-[:D {relation: 'subclass_of'}]->(b:N),
      (a)-[:D {relation: 'disjoint_class'}]->(b)
WHERE a.iri < b.iri
RETURN a.iri AS disjoint_a, b.iri AS disjoint_b, c.iri AS shared_subclass
ORDER BY disjoint_a, disjoint_b, shared_subclass
