// Declare the pizza ontology root and document prefixes.
// Every E edge carries an integer `position` (document order under its
// parent); `role` is query-facing decoration. Ontology child positions are
// assigned globally across migrations so the document order stays stable.

// Ontology(<https://example.org/pizza#>)
MERGE (ontology:N {uid: '0x01', kind: 'Ontology', ontology_iri: 'https://example.org/pizza#'})
MERGE (defaultPrefix:N {uid: '0x03', kind: 'Prefix', prefix_name: '', iri: 'https://example.org/pizza#'})
MERGE (owlPrefix:N {uid: '0x04', kind: 'Prefix', prefix_name: 'owl', iri: 'http://www.w3.org/2002/07/owl#'})
MERGE (rdfPrefix:N {uid: '0x05', kind: 'Prefix', prefix_name: 'rdf', iri: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})
MERGE (xmlPrefix:N {uid: '0x06', kind: 'Prefix', prefix_name: 'xml', iri: 'http://www.w3.org/XML/1998/namespace'})
MERGE (xsdPrefix:N {uid: '0x07', kind: 'Prefix', prefix_name: 'xsd', iri: 'http://www.w3.org/2001/XMLSchema#'})
MERGE (rdfsPrefix:N {uid: '0x08', kind: 'Prefix', prefix_name: 'rdfs', iri: 'http://www.w3.org/2000/01/rdf-schema#'})
MERGE (ontology)-[:E {role: 'prefix', position: 0}]->(defaultPrefix)
MERGE (ontology)-[:E {role: 'prefix', position: 1}]->(owlPrefix)
MERGE (ontology)-[:E {role: 'prefix', position: 2}]->(rdfPrefix)
MERGE (ontology)-[:E {role: 'prefix', position: 3}]->(xmlPrefix)
MERGE (ontology)-[:E {role: 'prefix', position: 4}]->(xsdPrefix)
MERGE (ontology)-[:E {role: 'prefix', position: 5}]->(rdfsPrefix);
