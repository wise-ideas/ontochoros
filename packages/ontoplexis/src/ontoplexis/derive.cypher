// Derivation rules for the derived-edge cache table D.
//
// One statement per OWL construct whose OWL 2 -> RDF mapping is a single
// triple (plus one marked convenience). Executed statement-by-statement by
// ontoplexis.derive.derive_edges after it clears D. The layer's semantics and
// the deliberate design decisions are documented in that module's docstring.
//
// Statements are separated by semicolons. Do not use semicolons anywhere else
// in this file (including comments).

// SubClassOf between named classes.
MATCH (ax:N {kind:'SubClassOf'})-[:E {role:'sub'}]->(a:N {kind:'Class'}),
      (ax)-[:E {role:'super'}]->(b:N {kind:'Class'})
WHERE a.iri IS NOT NULL AND b.iri IS NOT NULL
CREATE (a)-[:D {relation:'subclass_of'}]->(b);

// DisjointUnion members are subclasses of the union class.
MATCH (ax:N {kind:'DisjointUnion'})-[:E {role:'class'}]->(c:N {kind:'Class'}),
      (ax)-[:E {role:'operand'}]->(m:N {kind:'Class'})
WHERE c.iri IS NOT NULL AND m.iri IS NOT NULL
CREATE (m)-[:D {relation:'subclass_of'}]->(c);

MATCH (ax:N {kind:'EquivalentClasses'})-[:E {role:'operand'}]->(a:N {kind:'Class'}),
      (ax)-[:E {role:'operand'}]->(b:N {kind:'Class'})
WHERE a.iri IS NOT NULL AND b.iri IS NOT NULL AND a.uid <> b.uid
CREATE (a)-[:D {relation:'equivalent_class'}]->(b);

MATCH (ax)-[:E {role:'operand'}]->(a:N {kind:'Class'}),
      (ax)-[:E {role:'operand'}]->(b:N {kind:'Class'})
WHERE ax.kind IN ['DisjointClasses','DisjointUnion']
  AND a.iri IS NOT NULL AND b.iri IS NOT NULL AND a.uid <> b.uid
CREATE (a)-[:D {relation:'disjoint_class'}]->(b);

MATCH (ax)-[:E {role:'sub'}]->(a:N), (ax)-[:E {role:'super'}]->(b:N)
WHERE ax.kind IN ['SubObjectPropertyOf','SubDataPropertyOf','SubAnnotationPropertyOf']
  AND a.iri IS NOT NULL AND b.iri IS NOT NULL
CREATE (a)-[:D {relation:'subproperty_of'}]->(b);

MATCH (ax)-[:E {role:'operand'}]->(a:N), (ax)-[:E {role:'operand'}]->(b:N)
WHERE ax.kind IN ['EquivalentObjectProperties','EquivalentDataProperties']
  AND a.iri IS NOT NULL AND b.iri IS NOT NULL AND a.uid <> b.uid
CREATE (a)-[:D {relation:'equivalent_property'}]->(b);

MATCH (ax)-[:E {role:'operand'}]->(a:N), (ax)-[:E {role:'operand'}]->(b:N)
WHERE ax.kind IN ['DisjointObjectProperties','DisjointDataProperties']
  AND a.iri IS NOT NULL AND b.iri IS NOT NULL AND a.uid <> b.uid
CREATE (a)-[:D {relation:'disjoint_property'}]->(b);

MATCH (ax:N {kind:'InverseObjectProperties'})-[:E {role:'property'}]->(a:N),
      (ax)-[:E {role:'property'}]->(b:N)
WHERE a.iri IS NOT NULL AND b.iri IS NOT NULL AND a.uid <> b.uid
CREATE (a)-[:D {relation:'inverse_of'}]->(b);

// Unary property-characteristic axioms are single rdf:type triples
// (P rdf:type owl:FunctionalProperty and friends). There is no node for the
// OWL vocabulary class, so each becomes a self-loop on the property.
// FunctionalObjectProperty and FunctionalDataProperty share the 'functional'
// relation, mirroring the shared RDF vocabulary term.
MATCH (ax:N)-[:E {role:'property'}]->(p:N)
WHERE ax.kind IN ['FunctionalObjectProperty','FunctionalDataProperty',
                  'InverseFunctionalObjectProperty','ReflexiveObjectProperty',
                  'IrreflexiveObjectProperty','SymmetricObjectProperty',
                  'AsymmetricObjectProperty','TransitiveObjectProperty']
  AND p.iri IS NOT NULL
CREATE (p)-[:D {relation: CASE ax.kind
    WHEN 'FunctionalObjectProperty' THEN 'functional'
    WHEN 'FunctionalDataProperty' THEN 'functional'
    WHEN 'InverseFunctionalObjectProperty' THEN 'inverse_functional'
    WHEN 'ReflexiveObjectProperty' THEN 'reflexive'
    WHEN 'IrreflexiveObjectProperty' THEN 'irreflexive'
    WHEN 'SymmetricObjectProperty' THEN 'symmetric'
    WHEN 'AsymmetricObjectProperty' THEN 'asymmetric'
    ELSE 'transitive' END}]->(p);

MATCH (ax)-[:E {role:'property'}]->(p:N), (ax)-[:E {role:'domain'}]->(d:N)
WHERE ax.kind IN ['ObjectPropertyDomain','DataPropertyDomain','AnnotationPropertyDomain']
  AND p.iri IS NOT NULL AND d.iri IS NOT NULL
CREATE (p)-[:D {relation:'domain'}]->(d);

MATCH (ax)-[:E {role:'property'}]->(p:N), (ax)-[:E {role:'range'}]->(r:N)
WHERE ax.kind IN ['ObjectPropertyRange','DataPropertyRange','AnnotationPropertyRange']
  AND p.iri IS NOT NULL AND r.iri IS NOT NULL
CREATE (p)-[:D {relation:'range'}]->(r);

MATCH (ax:N {kind:'ClassAssertion'})-[:E {role:'class'}]->(c:N {kind:'Class'}),
      (ax)-[:E {role:'individual'}]->(i:N {kind:'NamedIndividual'})
WHERE c.iri IS NOT NULL AND i.iri IS NOT NULL
CREATE (i)-[:D {relation:'type'}]->(c);

MATCH (ax:N {kind:'ObjectPropertyAssertion'})-[:E {role:'property'}]->(p:N),
      (ax)-[:E {role:'subject'}]->(s:N {kind:'NamedIndividual'}),
      (ax)-[:E {role:'object'}]->(o:N {kind:'NamedIndividual'})
WHERE p.iri IS NOT NULL AND s.iri IS NOT NULL AND o.iri IS NOT NULL
CREATE (s)-[:D {relation:'asserts', property:p.iri}]->(o);

MATCH (ax:N {kind:'DataPropertyAssertion'})-[:E {role:'property'}]->(p:N),
      (ax)-[:E {role:'subject'}]->(s:N {kind:'NamedIndividual'}),
      (ax)-[:E {role:'object'}]->(v:N {kind:'Literal'})
WHERE p.iri IS NOT NULL AND s.iri IS NOT NULL
CREATE (s)-[:D {relation:'data_value', property:p.iri}]->(v);

MATCH (ax:N {kind:'SameIndividual'})-[:E {role:'operand'}]->(a:N),
      (ax)-[:E {role:'operand'}]->(b:N)
WHERE a.iri IS NOT NULL AND b.iri IS NOT NULL AND a.uid <> b.uid
CREATE (a)-[:D {relation:'same_as'}]->(b);

MATCH (ax:N {kind:'DifferentIndividuals'})-[:E {role:'operand'}]->(a:N),
      (ax)-[:E {role:'operand'}]->(b:N)
WHERE a.iri IS NOT NULL AND b.iri IS NOT NULL AND a.uid <> b.uid
CREATE (a)-[:D {relation:'different_from'}]->(b);

// AnnotationAssertion whose value is an IRI (seeAlso, replaced_by, ...).
// Subjects and IRI values name IRIs, not entities: the edge is attached to
// every entity node carrying the IRI, so punned entities each receive it.
MATCH (ax:N {kind:'AnnotationAssertion'})-[:E {role:'property'}]->(p:N),
      (ax)-[:E {role:'subject'}]->(s:N),
      (ax)-[:E {role:'value'}]->(v:N {kind:'IRI'})
MATCH (se:N) WHERE se.iri IS NOT NULL AND se.iri = s.text
MATCH (ve:N) WHERE ve.iri IS NOT NULL AND ve.iri = v.text
CREATE (se)-[:D {relation:'annotation', property:p.iri}]->(ve);

// AnnotationAssertion whose value is a literal (labels, comments, ...).
MATCH (ax:N {kind:'AnnotationAssertion'})-[:E {role:'property'}]->(p:N),
      (ax)-[:E {role:'subject'}]->(s:N),
      (ax)-[:E {role:'value'}]->(v:N {kind:'Literal'})
MATCH (se:N) WHERE se.iri IS NOT NULL AND se.iri = s.text
CREATE (se)-[:D {relation:'annotation_value', property:p.iri}]->(v);

// Marked convenience: NOT single-triple in RDF, but makes the existential
// content graph one hop.
MATCH (ax:N {kind:'SubClassOf'})-[:E {role:'sub'}]->(a:N {kind:'Class'}),
      (ax)-[:E {role:'super'}]->(r:N),
      (r)-[:E {role:'property'}]->(p:N),
      (r)-[:E {role:'filler'}]->(b:N {kind:'Class'})
WHERE r.kind IN ['ObjectSomeValuesFrom','ObjectAllValuesFrom']
  AND a.iri IS NOT NULL AND b.iri IS NOT NULL AND p.iri IS NOT NULL
CREATE (a)-[:D {relation:'restriction', property:p.iri,
                quantifier: CASE r.kind
                    WHEN 'ObjectSomeValuesFrom' THEN 'some' ELSE 'only' END}]->(b);
