// Subclass cycles: a chain of named classes A ⊑ B ⊑ … ⊑ A. Legal OWL — it collapses the
// members into one equivalence set — but almost always an accidental hierarchy-maintenance
// error rather than an intended equivalence. Reports each class that participates in a cycle.
//
// Cycle length is bounded to 5 with fixed-length patterns: real accidental cycles are short,
// and unbounded recursive traversal over the whole hierarchy is prohibitively slow on large
// ontologies. Each branch reports every member because the anchor rotates over all matches.
MATCH (a:N)-[:D {relation: 'subclass_of'}]->(:N)
      -[:D {relation: 'subclass_of'}]->(a)
RETURN DISTINCT a.iri AS iri
UNION
MATCH (a:N)-[:D {relation: 'subclass_of'}]->(:N)
      -[:D {relation: 'subclass_of'}]->(:N)
      -[:D {relation: 'subclass_of'}]->(a)
RETURN DISTINCT a.iri AS iri
UNION
MATCH (a:N)-[:D {relation: 'subclass_of'}]->(:N)
      -[:D {relation: 'subclass_of'}]->(:N)
      -[:D {relation: 'subclass_of'}]->(:N)
      -[:D {relation: 'subclass_of'}]->(a)
RETURN DISTINCT a.iri AS iri
UNION
MATCH (a:N)-[:D {relation: 'subclass_of'}]->(:N)
      -[:D {relation: 'subclass_of'}]->(:N)
      -[:D {relation: 'subclass_of'}]->(:N)
      -[:D {relation: 'subclass_of'}]->(:N)
      -[:D {relation: 'subclass_of'}]->(a)
RETURN DISTINCT a.iri AS iri
ORDER BY iri
