// The margherita individual and its three toppings.

// Ontology, classes, and properties from earlier migrations
MATCH
    (ontology:N {uid: '0x01'}),
    (Topping:N {uid: '0x11'}),
    (MargheritaPizza:N {uid: '0x12'}),
    (hasTopping:N {uid: '0x30'})

// NamedIndividual(:margherita), NamedIndividual(:tomatoSauce), NamedIndividual(:mozzarella), NamedIndividual(:basil)
MERGE (margherita:N {uid: '0x40', kind: 'NamedIndividual', iri: ':margherita'})
MERGE (tomatoSauce:N {uid: '0x41', kind: 'NamedIndividual', iri: ':tomatoSauce'})
MERGE (mozzarella:N {uid: '0x42', kind: 'NamedIndividual', iri: ':mozzarella'})
MERGE (basil:N {uid: '0x43', kind: 'NamedIndividual', iri: ':basil'})

// Declaration(NamedIndividual(:margherita))
MERGE (declMargherita:N {uid: '0x50', kind: 'Declaration'})
MERGE (declMargherita)-[:E {role: 'entity'}]->(margherita)
MERGE (ontology)-[:E {role: 'axioms'}]->(declMargherita)

// Declaration(NamedIndividual(:tomatoSauce))
MERGE (declTomatoSauce:N {uid: '0x51', kind: 'Declaration'})
MERGE (declTomatoSauce)-[:E {role: 'entity'}]->(tomatoSauce)
MERGE (ontology)-[:E {role: 'axioms'}]->(declTomatoSauce)

// Declaration(NamedIndividual(:mozzarella))
MERGE (declMozzarella:N {uid: '0x52', kind: 'Declaration'})
MERGE (declMozzarella)-[:E {role: 'entity'}]->(mozzarella)
MERGE (ontology)-[:E {role: 'axioms'}]->(declMozzarella)

// Declaration(NamedIndividual(:basil))
MERGE (declBasil:N {uid: '0x53', kind: 'Declaration'})
MERGE (declBasil)-[:E {role: 'entity'}]->(basil)
MERGE (ontology)-[:E {role: 'axioms'}]->(declBasil)

// ClassAssertion(:MargheritaPizza :margherita)
MERGE (classAssertionMargherita:N {uid: '0x60', kind: 'ClassAssertion'})
MERGE (classAssertionMargherita)-[:E {role: 'class_expression'}]->(MargheritaPizza)
MERGE (classAssertionMargherita)-[:E {role: 'individual'}]->(margherita)
MERGE (ontology)-[:E {role: 'axioms'}]->(classAssertionMargherita)

// ClassAssertion(:Topping :tomatoSauce)
MERGE (classAssertionTomato:N {uid: '0x61', kind: 'ClassAssertion'})
MERGE (classAssertionTomato)-[:E {role: 'class_expression'}]->(Topping)
MERGE (classAssertionTomato)-[:E {role: 'individual'}]->(tomatoSauce)
MERGE (ontology)-[:E {role: 'axioms'}]->(classAssertionTomato)

// ClassAssertion(:Topping :mozzarella)
MERGE (classAssertionMozzarella:N {uid: '0x62', kind: 'ClassAssertion'})
MERGE (classAssertionMozzarella)-[:E {role: 'class_expression'}]->(Topping)
MERGE (classAssertionMozzarella)-[:E {role: 'individual'}]->(mozzarella)
MERGE (ontology)-[:E {role: 'axioms'}]->(classAssertionMozzarella)

// ClassAssertion(:Topping :basil)
MERGE (classAssertionBasil:N {uid: '0x63', kind: 'ClassAssertion'})
MERGE (classAssertionBasil)-[:E {role: 'class_expression'}]->(Topping)
MERGE (classAssertionBasil)-[:E {role: 'individual'}]->(basil)
MERGE (ontology)-[:E {role: 'axioms'}]->(classAssertionBasil)

// ObjectPropertyAssertion(:hasTopping :margherita :tomatoSauce)
MERGE (hasToppingTomato:N {uid: '0x70', kind: 'ObjectPropertyAssertion'})
MERGE (hasToppingTomato)-[:E {role: 'source_individual'}]->(margherita)
MERGE (hasToppingTomato)-[:E {role: 'object_property_expression'}]->(hasTopping)
MERGE (hasToppingTomato)-[:E {role: 'target_individual'}]->(tomatoSauce)
MERGE (ontology)-[:E {role: 'axioms'}]->(hasToppingTomato)

// ObjectPropertyAssertion(:hasTopping :margherita :mozzarella)
MERGE (hasToppingMozzarella:N {uid: '0x71', kind: 'ObjectPropertyAssertion'})
MERGE (hasToppingMozzarella)-[:E {role: 'source_individual'}]->(margherita)
MERGE (hasToppingMozzarella)-[:E {role: 'object_property_expression'}]->(hasTopping)
MERGE (hasToppingMozzarella)-[:E {role: 'target_individual'}]->(mozzarella)
MERGE (ontology)-[:E {role: 'axioms'}]->(hasToppingMozzarella)

// ObjectPropertyAssertion(:hasTopping :margherita :basil)
MERGE (hasToppingBasil:N {uid: '0x72', kind: 'ObjectPropertyAssertion'})
MERGE (hasToppingBasil)-[:E {role: 'source_individual'}]->(margherita)
MERGE (hasToppingBasil)-[:E {role: 'object_property_expression'}]->(hasTopping)
MERGE (hasToppingBasil)-[:E {role: 'target_individual'}]->(basil)
MERGE (ontology)-[:E {role: 'axioms'}]->(hasToppingBasil);
