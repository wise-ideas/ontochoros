// A class asserted (not inferred) to be a subclass of owl:Nothing.
// In the asserted graph this is always a modelling mistake; classify with an
// external reasoner first if you want to catch inferred unsatisfiability instead.
//
// ROBOT equivalent:
//   robot verify --input onto.owl \
//     --queries explicit_nothing_subclass.sparql
//   -- where explicit_nothing_subclass.sparql contains:
//   SELECT ?class WHERE { ?class rdfs:subClassOf owl:Nothing . }
MATCH
  (a:N {kind: 'SubClassOf'})-[:E {role: 'super'}]->(nothing:N),
  (a)-[:E {role: 'sub'}]->(sub:N)
WHERE nothing.iri = 'http://www.w3.org/2002/07/owl#Nothing'
RETURN sub.iri AS class_iri
