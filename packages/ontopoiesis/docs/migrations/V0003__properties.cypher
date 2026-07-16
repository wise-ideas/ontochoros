// hasTopping property with domain Pizza and range Topping.

// Ontology and classes from earlier migrations
MATCH
    (ontology:N {uid: '0x01'}),
    (Pizza:N {uid: '0x10'}),
    (Topping:N {uid: '0x11'})

// ObjectProperty(:hasTopping)
MERGE (hasTopping:N {uid: '0x30', kind: 'ObjectProperty', iri: 'https://example.org/pizza#hasTopping'})

// Declaration(ObjectProperty(:hasTopping))
MERGE (declHasTopping:N {uid: '0x31', kind: 'Declaration'})
MERGE (declHasTopping)-[:E {role: 'entity', position: 0}]->(hasTopping)
MERGE (ontology)-[:E {role: 'axiom', position: 10}]->(declHasTopping)

// ObjectPropertyDomain(:hasTopping :Pizza)
MERGE (objectPropertyDomain:N {uid: '0x32', kind: 'ObjectPropertyDomain'})
MERGE (objectPropertyDomain)-[:E {role: 'property', position: 0}]->(hasTopping)
MERGE (objectPropertyDomain)-[:E {role: 'domain', position: 1}]->(Pizza)
MERGE (ontology)-[:E {role: 'axiom', position: 11}]->(objectPropertyDomain)

// ObjectPropertyRange(:hasTopping :Topping)
MERGE (objectPropertyRange:N {uid: '0x33', kind: 'ObjectPropertyRange'})
MERGE (objectPropertyRange)-[:E {role: 'property', position: 0}]->(hasTopping)
MERGE (objectPropertyRange)-[:E {role: 'range', position: 1}]->(Topping)
MERGE (ontology)-[:E {role: 'axiom', position: 12}]->(objectPropertyRange);
