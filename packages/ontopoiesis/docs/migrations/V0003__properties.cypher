// hasTopping property with domain Pizza and range Topping.

// Ontology and classes from earlier migrations
MATCH
    (ontology:N {uid: '0x01'}),
    (Pizza:N {uid: '0x10'}),
    (Topping:N {uid: '0x11'})

// ObjectProperty(:hasTopping)
MERGE (hasTopping:N {uid: '0x30', kind: 'ObjectProperty', iri: ':hasTopping'})

// Declaration(ObjectProperty(:hasTopping))
MERGE (declHasTopping:N {uid: '0x31', kind: 'Declaration'})
MERGE (declHasTopping)-[:E {role: 'entity'}]->(hasTopping)
MERGE (ontology)-[:E {role: 'axioms'}]->(declHasTopping)

// ObjectPropertyDomain(:hasTopping :Pizza)
MERGE (objectPropertyDomain:N {uid: '0x32', kind: 'ObjectPropertyDomain'})
MERGE (objectPropertyDomain)-[:E {role: 'object_property_expression'}]->(hasTopping)
MERGE (objectPropertyDomain)-[:E {role: 'domain'}]->(Pizza)
MERGE (ontology)-[:E {role: 'axioms'}]->(objectPropertyDomain)

// ObjectPropertyRange(:hasTopping :Topping)
MERGE (objectPropertyRange:N {uid: '0x33', kind: 'ObjectPropertyRange'})
MERGE (objectPropertyRange)-[:E {role: 'object_property_expression'}]->(hasTopping)
MERGE (objectPropertyRange)-[:E {role: 'range'}]->(Topping)
MERGE (ontology)-[:E {role: 'axioms'}]->(objectPropertyRange);
