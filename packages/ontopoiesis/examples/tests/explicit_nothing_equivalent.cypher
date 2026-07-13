// A named class explicitly declared equivalent to owl:Nothing in the asserted graph.
// This makes the class permanently unsatisfiable regardless of other axioms.
//
// ROBOT equivalent:
//   robot verify --input onto.owl \
//     --queries explicit_nothing_equivalent.sparql
//   -- where explicit_nothing_equivalent.sparql contains:
//   SELECT ?class WHERE { ?class owl:equivalentClass owl:Nothing . }
MATCH
  (a:N {kind: 'EquivalentClasses'})-[:E {role: 'operand'}]->(nothing:N),
  (a)-[:E {role: 'operand'}]->(other:N)
WHERE
  nothing.iri = 'http://www.w3.org/2002/07/owl#Nothing' AND
  other.iri <> 'http://www.w3.org/2002/07/owl#Nothing'
RETURN other.iri AS class_iri
