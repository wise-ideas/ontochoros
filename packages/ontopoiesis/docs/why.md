---
title: "Why Ontopoiesis"
---

# Why Ontopoiesis

Ontologies are usually managed like documents: edited in a GUI, reviewed by
eyeball, validated by a specialist. Ontopoiesis manages them like code.

- **A projection is a database.** ontoplexis loads OWL/XML into an embedded
  Ladybug graph whose shape *is* the OWL 2 structural specification. Every
  question about the ontology becomes a Cypher query.
- **Quality gates are queries.** Lint rules and tests are plain `.cypher`
  files; a rule fails when it returns rows. Teams extend the rule set the
  same way they write dbt tests.
- **Changes are reviewable.** `diff` fingerprints every axiom structurally,
  so a pull request shows exactly which constructs were added or removed.
- **Edits are migrations.** Graph-native Cypher migration scripts, applied
  in order and recorded in the projection, replace hand-editing XML.

The intended audience is data engineers who already know SQL-shaped
workflows — lint, test, diff, CI — and want to own an ontology without
specialist tooling. Reasoning and format conversion stay with the external
tools that already do them well (ROBOT, Protégé, your reasoner of choice).
