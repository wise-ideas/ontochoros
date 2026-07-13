// Pizza and Topping classes with one subclass axiom.

// Ontology from earlier migration
MATCH (ontology:N {uid: '0x01'})

// Class(:Pizza), Class(:Topping), Class(:MargheritaPizza)
MERGE (Pizza:N {uid: '0x10', kind: 'Class', iri: ':Pizza'})
MERGE (Topping:N {uid: '0x11', kind: 'Class', iri: ':Topping'})
MERGE (MargheritaPizza:N {uid: '0x12', kind: 'Class', iri: ':MargheritaPizza'})

// Declaration(Class(:Pizza))
MERGE (declPizza:N {uid: '0x20', kind: 'Declaration'})
MERGE (declPizza)-[:E {role: 'entity'}]->(Pizza)
MERGE (ontology)-[:E {role: 'axioms'}]->(declPizza)

// Declaration(Class(:Topping))
MERGE (declTopping:N {uid: '0x21', kind: 'Declaration'})
MERGE (declTopping)-[:E {role: 'entity'}]->(Topping)
MERGE (ontology)-[:E {role: 'axioms'}]->(declTopping)

// Declaration(Class(:MargheritaPizza))
MERGE (declMargherita:N {uid: '0x22', kind: 'Declaration'})
MERGE (declMargherita)-[:E {role: 'entity'}]->(MargheritaPizza)
MERGE (ontology)-[:E {role: 'axioms'}]->(declMargherita)

// SubClassOf(:MargheritaPizza :Pizza)
MERGE (subClassOf:N {uid: '0x23', kind: 'SubClassOf'})
MERGE (subClassOf)-[:E {role: 'sub_class_expression'}]->(MargheritaPizza)
MERGE (subClassOf)-[:E {role: 'super_class_expression'}]->(Pizza)
MERGE (ontology)-[:E {role: 'axioms'}]->(subClassOf);
