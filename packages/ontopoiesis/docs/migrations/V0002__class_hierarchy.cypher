// Pizza and Topping classes with one subclass axiom.

// Ontology from earlier migration
MATCH (ontology:N {uid: '0x01'})

// Class(:Pizza), Class(:Topping), Class(:MargheritaPizza)
MERGE (Pizza:N {uid: '0x10', kind: 'Class', iri: 'https://example.org/pizza#Pizza'})
MERGE (Topping:N {uid: '0x11', kind: 'Class', iri: 'https://example.org/pizza#Topping'})
MERGE (MargheritaPizza:N {uid: '0x12', kind: 'Class', iri: 'https://example.org/pizza#MargheritaPizza'})

// Declaration(Class(:Pizza))
MERGE (declPizza:N {uid: '0x20', kind: 'Declaration'})
MERGE (declPizza)-[:E {role: 'entity', position: 0}]->(Pizza)
MERGE (ontology)-[:E {role: 'axiom', position: 6}]->(declPizza)

// Declaration(Class(:Topping))
MERGE (declTopping:N {uid: '0x21', kind: 'Declaration'})
MERGE (declTopping)-[:E {role: 'entity', position: 0}]->(Topping)
MERGE (ontology)-[:E {role: 'axiom', position: 7}]->(declTopping)

// Declaration(Class(:MargheritaPizza))
MERGE (declMargherita:N {uid: '0x22', kind: 'Declaration'})
MERGE (declMargherita)-[:E {role: 'entity', position: 0}]->(MargheritaPizza)
MERGE (ontology)-[:E {role: 'axiom', position: 8}]->(declMargherita)

// SubClassOf(:MargheritaPizza :Pizza)
MERGE (subClassOf:N {uid: '0x23', kind: 'SubClassOf'})
MERGE (subClassOf)-[:E {role: 'sub', position: 0}]->(MargheritaPizza)
MERGE (subClassOf)-[:E {role: 'super', position: 1}]->(Pizza)
MERGE (ontology)-[:E {role: 'axiom', position: 9}]->(subClassOf);
