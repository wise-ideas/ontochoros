from ontoplexus.graph import build_projection_database, compile_projection_graph
from ontoplexus.model.records import coerce_construct

BASE = "https://example.org/pizza#"

records = [
    coerce_construct(
        {
            "uid": "0x01",
            "construct": {
                "kind": "Ontology",
                "ontology_iri": f"{BASE}ontology",
                "version_iri": None,
                "directly_imports_documents": [],
                "ontology_annotations": [],
                "axioms": [],
            },
        }
    ),
    coerce_construct({"uid": "0x10", "construct": {"kind": "Class", "iri": f"{BASE}Pizza"}}),
    coerce_construct({"uid": "0x11", "construct": {"kind": "Class", "iri": f"{BASE}Topping"}}),
    coerce_construct(
        {"uid": "0x12", "construct": {"kind": "Class", "iri": f"{BASE}MargheritaPizza"}}
    ),
    coerce_construct(
        {
            "uid": "0x20",
            "construct": {
                "kind": "SubClassOf",
                "sub_class_expression": {"uid": "0x12"},
                "super_class_expression": {"uid": "0x10"},
                "axiom_annotations": [],
            },
        }
    ),
]

graph = compile_projection_graph(records)
with build_projection_database(records) as projection:
    result = projection.execute("MATCH (n:N) WHERE n.kind = 'Class' RETURN n.iri ORDER BY n.iri")

for row in result.rows:
    print(row["n.iri"])
