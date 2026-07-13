---
title: "Installation"
---

# Installation

Ontopoiesis is a Python package (3.11+), pure Python at runtime.

```bash
pip install ontopoiesis
# or, in a uv project
uv add ontopoiesis
```

This installs the `ontopoiesis` CLI and its dependencies, including
[ontoplexis](https://wise-ideas.github.io/ontotheke/ontoplexis/) (the OWL/XML ⇄
projection core) and the embedded Ladybug database.

Optional extras:

- **Graphviz** — required only for `ontopoiesis render ... -o out.png`
  (SVG and DOT rendering are pure Python).
- **ROBOT / Protégé** — to convert other OWL serializations to OWL/XML
  before `build`, and for reasoning.

Check the install:

```bash
ontopoiesis --help
```
