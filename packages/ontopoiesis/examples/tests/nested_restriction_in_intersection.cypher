// Classes whose necessary condition is an intersection that includes a
// someValuesFrom restriction — the pattern ClassName ⊑ A ⊓ ∃P.B.
// Returns the class and the restricted property so the reviewer can audit
// whether the restriction is intentional or an artefact of a merge.
//
// SPARQL requires three layers of blank-node traversal:
//   SELECT ?class ?property WHERE {
//     ?class rdfs:subClassOf ?intersection .
//     ?intersection owl:intersectionOf/rdf:rest*/rdf:first ?restriction .
//     ?restriction rdf:type owl:Restriction ;
//       owl:onProperty ?property ;
//       owl:someValuesFrom ?filler .
//   }
// The rdf:rest* property path is not supported in all SPARQL engines and
// produces unpredictable results when lists are malformed or partially
// materialised. The Cypher role traverses typed expression nodes directly.
MATCH
  (a:N {kind: 'SubClassOf'})-[:E {role: 'super'}]->(i:N {kind: 'ObjectIntersectionOf'}),
  (i)-[:E {role: 'operand'}]->(r:N {kind: 'ObjectSomeValuesFrom'}),
  (r)-[:E {role: 'property'}]->(prop:N),
  (a)-[:E {role: 'sub'}]->(sub:N)
RETURN sub.iri AS class_iri, prop.iri AS restriction_property
