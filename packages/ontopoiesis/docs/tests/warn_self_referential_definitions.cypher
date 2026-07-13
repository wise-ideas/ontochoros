MATCH (ax:N {kind: 'EquivalentClasses'})
      -[:E {role: 'class_expressions'}]->(named_class:N {kind: 'Class'}),
      (ax)-[:E {role: 'class_expressions'}]->(:N {kind: 'ObjectHasSelf'})
RETURN named_class.iri AS class
ORDER BY class
