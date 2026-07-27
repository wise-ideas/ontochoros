// Classes and properties must have a Declaration axiom in the axiom closure.
// NamedIndividual is intentionally absent: OWL 2 DL permits individuals to
// occur without declarations.
// Entities from the OWL 2 built-in namespaces (owl:, rdfs:, rdf:) are
// pre-declared by the OWL 2 spec and never require explicit Declarations.
MATCH (e:N)
WHERE
  e.kind IN [
    'Class',
    'ObjectProperty',
    'DataProperty',
    'AnnotationProperty'
  ]
  AND e.iri IS NOT NULL
  AND NOT e.iri STARTS WITH 'http://www.w3.org/2002/07/owl#'
  AND NOT e.iri STARTS WITH 'http://www.w3.org/2000/01/rdf-schema#'
  AND NOT e.iri STARTS WITH 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  AND NOT EXISTS {
    MATCH (:N {kind: 'Declaration'})-[:E {role: 'entity'}]->(e)
  }
RETURN e.kind AS kind, e.iri AS iri

UNION ALL

// User-defined datatypes (those with a DatatypeDefinition axiom) must also be
// declared. Built-in XSD/RDF/OWL datatypes are pre-declared by the OWL 2 spec
// and are intentionally excluded here by only checking for DatatypeDefinition.
MATCH (e:N {kind: 'Datatype'})
WHERE
  e.iri IS NOT NULL
  AND EXISTS {
    MATCH (:N {kind: 'DatatypeDefinition'})-[:E {role: 'datatype'}]->(e)
  }
  AND NOT EXISTS {
    MATCH (:N {kind: 'Declaration'})-[:E {role: 'entity'}]->(e)
  }
RETURN
  e.kind AS kind,
  e.iri AS iri

ORDER BY kind, iri
