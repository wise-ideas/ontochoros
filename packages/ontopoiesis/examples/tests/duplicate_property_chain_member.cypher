// A property appearing more than once at different positions in the same
// ObjectPropertyChain. The chain P ∘ P → R is almost always a copy-paste
// error; a genuine self-composition would be modelled differently.
//
// SPARQL has no clean equivalent. rdf:rest*/rdf:first traverses the chain
// list but does not expose position, so detecting the same property at two
// distinct positions requires a self-join over the list structure that
// is fragile and rarely works across serialisers.
MATCH
  (chain:N {kind: 'ObjectPropertyChain'})-[e1:E {role: 'operand'}]->(p:N),
  (chain)-[e2:E {role: 'operand'}]->(p)
WHERE e1.position < e2.position
RETURN chain.uid AS chain_uid, p.iri AS duplicate_property
