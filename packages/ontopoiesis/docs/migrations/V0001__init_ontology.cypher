// Declare the pizza ontology root and document prefixes.

// Ontology(<https://example.org/pizza#>)
MERGE (ontology:N {uid: '0x01', kind: 'Ontology', ontology_iri: 'https://example.org/pizza#'})
MERGE (ontologyDocument:N {uid: '0x02', kind: 'OntologyDocument'})
MERGE (defaultPrefix:N {uid: '0x03', kind: 'Prefix', prefix_name: ':', full_iri: 'https://example.org/pizza#'})
MERGE (owlPrefix:N {uid: '0x04', kind: 'Prefix', prefix_name: 'owl:', full_iri: 'http://www.w3.org/2002/07/owl#'})
MERGE (rdfPrefix:N {uid: '0x05', kind: 'Prefix', prefix_name: 'rdf:', full_iri: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})
MERGE (xmlPrefix:N {uid: '0x06', kind: 'Prefix', prefix_name: 'xml:', full_iri: 'http://www.w3.org/XML/1998/namespace'})
MERGE (xsdPrefix:N {uid: '0x07', kind: 'Prefix', prefix_name: 'xsd:', full_iri: 'http://www.w3.org/2001/XMLSchema#'})
MERGE (rdfsPrefix:N {uid: '0x08', kind: 'Prefix', prefix_name: 'rdfs:', full_iri: 'http://www.w3.org/2000/01/rdf-schema#'})
MERGE (ontologyDocument)-[:E {role: 'ontology'}]->(ontology)
MERGE (ontologyDocument)-[:E {role: 'prefix_declarations', endpoint_order: 1}]->(defaultPrefix)
MERGE (ontologyDocument)-[:E {role: 'prefix_declarations', endpoint_order: 2}]->(owlPrefix)
MERGE (ontologyDocument)-[:E {role: 'prefix_declarations', endpoint_order: 3}]->(rdfPrefix)
MERGE (ontologyDocument)-[:E {role: 'prefix_declarations', endpoint_order: 4}]->(xmlPrefix)
MERGE (ontologyDocument)-[:E {role: 'prefix_declarations', endpoint_order: 5}]->(xsdPrefix)
MERGE (ontologyDocument)-[:E {role: 'prefix_declarations', endpoint_order: 6}]->(rdfsPrefix);
