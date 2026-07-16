{%- macro subclass(sub_iri, super_iri) %}
MATCH
    (sub:N  {iri: '<< sub_iri >>'}),
    (super:N {iri: '<< super_iri >>'})
MERGE (axiom:N {
    uid: '<< axiom_uid("SubClassOf", [("sub", scalar_uid("Class", sub_iri)),
                                      ("super", scalar_uid("Class", super_iri))]) >>',
    kind: 'SubClassOf'
})
MERGE (axiom)-[:E {role: 'sub', position: 0}]->(sub)
MERGE (axiom)-[:E {role: 'super', position: 1}]->(super)
{%- endmacro %}

// Assert the pizza class hierarchy.
<< subclass("https://example.org/pizza#MargheritaPizza", "https://example.org/pizza#Pizza") >>;
<< subclass("https://example.org/pizza#Pizza",           "https://www.w3.org/2002/07/owl#Thing") >>;
