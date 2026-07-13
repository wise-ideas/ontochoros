// SubClassOf axioms carrying an owl:deprecated axiom annotation — flagged
// for removal but not yet deleted. Returns the sub/super class pair so the
// reviewer knows which relationship is deprecated.
//
// SPARQL equivalent requires the owl:Axiom reification pattern:
//   SELECT ?sub ?super WHERE {
//     ?annotation rdf:type owl:Axiom ;
//       owl:annotatedSource ?sub ;
//       owl:annotatedProperty rdfs:subClassOf ;
//       owl:annotatedTarget ?super ;
//       owl:deprecated true .
//   }
// Not all serialisers emit owl:Axiom reification for axiom annotations,
// making this query brittle across tools. The Cypher role is direct because
// axiom nodes carry their annotation edges regardless of serialisation format.
MATCH
  (a:N {kind: 'SubClassOf'})-[:E {role: 'annotation'}]->(ann:N {kind: 'Annotation'}),
  (ann)-[:E {role: 'property'}]->(:N {iri: 'http://www.w3.org/2002/07/owl#deprecated'}),
  (a)-[:E {role: 'sub'}]->(sub:N),
  (a)-[:E {role: 'super'}]->(sup:N)
RETURN sub.iri AS sub_class, sup.iri AS super_class
