"""Docs cypher snippets are executed so the documented model cannot drift.

Every fenced ``cypher`` block in the docs runs against a real projection built
from the bundled family ontology (derived edges included, as in any built
projection). Queries that reference IRIs from other sample ontologies simply
return no rows — the gate is that every snippet compiles and runs against the
actual ``N``/``E``/``D`` schema.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from ontoplexis import Ontology, WritableProjection

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DOCS = PACKAGE_ROOT / "docs"

_FENCE = re.compile(r"^```(\w+)[^\n]*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
_INCLUDE = re.compile(r'^--8<-- "(?P<path>[^"]+)"$', re.MULTILINE)

#: Values supplied for ``$``-parameters appearing in cypher blocks.
_PARAMETER_VALUES: dict[str, object] = {"iri": "http://example.org/x#A"}

_WRITE_CLAUSE = re.compile(r"\b(CREATE|MERGE|SET|DELETE|DETACH|COPY|ALTER|DROP)\b", re.IGNORECASE)


def _expand_includes(block: str) -> str:
    """Inline pymdownx-snippets markers, resolved like the docs build does."""
    return _INCLUDE.sub(
        lambda m: (PACKAGE_ROOT / m.group("path")).read_text(encoding="utf-8"), block
    )


def _blocks(path: Path, language: str) -> list[str]:
    return [
        _expand_includes(match.group(2))
        for match in _FENCE.finditer(path.read_text(encoding="utf-8"))
        if match.group(1) == language
    ]


def _docs_with(language: str) -> list[Path]:
    return sorted(p for p in DOCS.rglob("*.md") if _blocks(p, language))


@pytest.mark.parametrize("doc", _docs_with("cypher"), ids=lambda p: str(p.relative_to(DOCS)))
def test_cypher_snippets_execute(doc: Path, tmp_path) -> None:
    target = str(tmp_path / "docs.lbug")
    document = (DOCS / "family.owlxml").read_text(encoding="utf-8")
    Ontology.from_owlxml(document).save_projection(target).close()
    with WritableProjection.open(target) as projection:
        for index, block in enumerate(_blocks(doc, "cypher")):
            if any(marker in block for marker in ("{{", "{%", "<<")):
                continue  # migration-template source; not raw Cypher
            # Strip whole-line comments before splitting: comment prose may
            # contain semicolons. (`//` inside string literals — IRIs — is
            # never at the start of a line, so it survives.)
            code = re.sub(r"(?m)^\s*//.*$", "", block)
            for statement in filter(None, (s.strip() for s in code.split(";"))):
                if statement.upper().startswith("MATCH") and not (
                    "RETURN" in statement.upper() or _WRITE_CLAUSE.search(statement)
                ):
                    # Illustrative pattern fragment: complete it so the parser
                    # still validates the pattern against the schema.
                    statement += "\nRETURN count(*) AS _fragment_check"
                parameters = {
                    name: value
                    for name, value in _PARAMETER_VALUES.items()
                    if f"${name}" in statement
                } or None
                try:
                    projection.execute(statement, parameters=parameters)
                except Exception as exc:  # pragma: no cover - failure reporting
                    pytest.fail(f"{doc.name} cypher block #{index} failed: {exc}\n---\n{statement}")
