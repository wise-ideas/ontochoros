// The margherita individual and its three toppings.

// Ontology, classes, and properties from earlier migrations
MATCH
    (ontology:N {uid: '0x01'}),
    (Topping:N {uid: '0x11'}),
    (MargheritaPizza:N {uid: '0x12'}),
    (hasTopping:N {uid: '0x30'})

// NamedIndividual(:margherita), NamedIndividual(:tomatoSauce), NamedIndividual(:mozzarella), NamedIndividual(:basil)
MERGE (margherita:N {uid: '0x40', kind: 'NamedIndividual', iri: 'https://example.org/pizza#margherita'})
MERGE (tomatoSauce:N {uid: '0x41', kind: 'NamedIndividual', iri: 'https://example.org/pizza#tomatoSauce'})
MERGE (mozzarella:N {uid: '0x42', kind: 'NamedIndividual', iri: 'https://example.org/pizza#mozzarella'})
MERGE (basil:N {uid: '0x43', kind: 'NamedIndividual', iri: 'https://example.org/pizza#basil'})

// Declaration(NamedIndividual(:margherita))
MERGE (declMargherita:N {uid: '0x50', kind: 'Declaration'})
MERGE (declMargherita)-[:E {role: 'entity', position: 0}]->(margherita)
MERGE (ontology)-[:E {role: 'axiom', position: 13}]->(declMargherita)

// Declaration(NamedIndividual(:tomatoSauce))
MERGE (declTomatoSauce:N {uid: '0x51', kind: 'Declaration'})
MERGE (declTomatoSauce)-[:E {role: 'entity', position: 0}]->(tomatoSauce)
MERGE (ontology)-[:E {role: 'axiom', position: 14}]->(declTomatoSauce)

// Declaration(NamedIndividual(:mozzarella))
MERGE (declMozzarella:N {uid: '0x52', kind: 'Declaration'})
MERGE (declMozzarella)-[:E {role: 'entity', position: 0}]->(mozzarella)
MERGE (ontology)-[:E {role: 'axiom', position: 15}]->(declMozzarella)

// Declaration(NamedIndividual(:basil))
MERGE (declBasil:N {uid: '0x53', kind: 'Declaration'})
MERGE (declBasil)-[:E {role: 'entity', position: 0}]->(basil)
MERGE (ontology)-[:E {role: 'axiom', position: 16}]->(declBasil)

// ClassAssertion(:MargheritaPizza :margherita)
MERGE (classAssertionMargherita:N {uid: '0x60', kind: 'ClassAssertion'})
MERGE (classAssertionMargherita)-[:E {role: 'class', position: 0}]->(MargheritaPizza)
MERGE (classAssertionMargherita)-[:E {role: 'individual', position: 1}]->(margherita)
MERGE (ontology)-[:E {role: 'axiom', position: 17}]->(classAssertionMargherita)

// ClassAssertion(:Topping :tomatoSauce)
MERGE (classAssertionTomato:N {uid: '0x61', kind: 'ClassAssertion'})
MERGE (classAssertionTomato)-[:E {role: 'class', position: 0}]->(Topping)
MERGE (classAssertionTomato)-[:E {role: 'individual', position: 1}]->(tomatoSauce)
MERGE (ontology)-[:E {role: 'axiom', position: 18}]->(classAssertionTomato)

// ClassAssertion(:Topping :mozzarella)
MERGE (classAssertionMozzarella:N {uid: '0x62', kind: 'ClassAssertion'})
MERGE (classAssertionMozzarella)-[:E {role: 'class', position: 0}]->(Topping)
MERGE (classAssertionMozzarella)-[:E {role: 'individual', position: 1}]->(mozzarella)
MERGE (ontology)-[:E {role: 'axiom', position: 19}]->(classAssertionMozzarella)

// ClassAssertion(:Topping :basil)
MERGE (classAssertionBasil:N {uid: '0x63', kind: 'ClassAssertion'})
MERGE (classAssertionBasil)-[:E {role: 'class', position: 0}]->(Topping)
MERGE (classAssertionBasil)-[:E {role: 'individual', position: 1}]->(basil)
MERGE (ontology)-[:E {role: 'axiom', position: 20}]->(classAssertionBasil)

// ObjectPropertyAssertion(:hasTopping :margherita :tomatoSauce)
MERGE (hasToppingTomato:N {uid: '0x70', kind: 'ObjectPropertyAssertion'})
MERGE (hasToppingTomato)-[:E {role: 'property', position: 0}]->(hasTopping)
MERGE (hasToppingTomato)-[:E {role: 'subject', position: 1}]->(margherita)
MERGE (hasToppingTomato)-[:E {role: 'object', position: 2}]->(tomatoSauce)
MERGE (ontology)-[:E {role: 'axiom', position: 21}]->(hasToppingTomato)

// ObjectPropertyAssertion(:hasTopping :margherita :mozzarella)
MERGE (hasToppingMozzarella:N {uid: '0x71', kind: 'ObjectPropertyAssertion'})
MERGE (hasToppingMozzarella)-[:E {role: 'property', position: 0}]->(hasTopping)
MERGE (hasToppingMozzarella)-[:E {role: 'subject', position: 1}]->(margherita)
MERGE (hasToppingMozzarella)-[:E {role: 'object', position: 2}]->(mozzarella)
MERGE (ontology)-[:E {role: 'axiom', position: 22}]->(hasToppingMozzarella)

// ObjectPropertyAssertion(:hasTopping :margherita :basil)
MERGE (hasToppingBasil:N {uid: '0x72', kind: 'ObjectPropertyAssertion'})
MERGE (hasToppingBasil)-[:E {role: 'property', position: 0}]->(hasTopping)
MERGE (hasToppingBasil)-[:E {role: 'subject', position: 1}]->(margherita)
MERGE (hasToppingBasil)-[:E {role: 'object', position: 2}]->(basil)
MERGE (ontology)-[:E {role: 'axiom', position: 23}]->(hasToppingBasil);
