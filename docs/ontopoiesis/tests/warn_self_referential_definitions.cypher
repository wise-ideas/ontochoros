MATCH (ax:N {kind: 'EquivalentClasses'})
      -[:E {role: 'operand'}]->(named_class:N {kind: 'Class'}),
      (ax)-[:E {role: 'operand'}]->(:N {kind: 'ObjectHasSelf'})
RETURN named_class.iri AS class
ORDER BY class
