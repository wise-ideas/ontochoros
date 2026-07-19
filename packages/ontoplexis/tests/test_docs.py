"""Docs snippets are executed so the documented model cannot silently drift.

Every fenced ``python`` block runs top-to-bottom per document (a shared
namespace per file, mirroring a reader following along), and every fenced
``cypher`` block executes against a real projection. Blocks share the sample
files the docs themselves reference: ``animals.owlxml`` is extracted from the
quickstart's own ``xml`` fence, and other referenced documents are seeded with
the bundled family ontology (the content only needs to be valid OWL/XML).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ontoplexis import Ontology, WritableProjection

# The package's user docs live in the monorepo-root docs tree.
DOCS = Path(__file__).resolve().parents[3] / "docs" / "ontoplexis"

_FENCE = re.compile(r"^```(\w+)[^\n]*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)

#: Values supplied for ``$``-parameters appearing in cypher blocks. A parameter
#: that matches nothing in the sample data simply returns no rows, which is
#: fine — the gate is that the query compiles and runs against the schema.
_PARAMETER_VALUES: dict[str, object] = {"iri": "http://example.org/x#A"}


def _blocks(path: Path, language: str) -> list[str]:
    return [
        match.group(2)
        for match in _FENCE.finditer(path.read_text(encoding="utf-8"))
        if match.group(1) == language
    ]


def _docs_with(language: str) -> list[Path]:
    # A gate that discovers its own inputs must fail loudly when it finds
    # none: an empty parametrize set silently skips, which is how a docs
    # reorganization once disabled this test without anyone noticing.
    docs = sorted(p for p in DOCS.rglob("*.md") if _blocks(p, language))
    if not docs:
        raise AssertionError(f"No docs with ```{language} blocks found under {DOCS}")
    return docs


def _seed_sample_files(target: Path) -> None:
    family = (DOCS / "family.owlxml").read_text(encoding="utf-8")
    quickstart_xml = _blocks(DOCS / "quickstart.md", "xml")
    (target / "animals.owlxml").write_text(
        quickstart_xml[0] if quickstart_xml else family, encoding="utf-8"
    )
    (target / "pizza.owx").write_text(family, encoding="utf-8")


@pytest.mark.parametrize("doc", _docs_with("python"), ids=lambda p: str(p.relative_to(DOCS)))
def test_python_snippets_execute(doc: Path, tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _seed_sample_files(tmp_path)
    # Some snippets continue from prose context ("given a path to a
    # document..."); the namespace provides that ambient context.
    namespace: dict[str, object] = {"path": Path("animals.owlxml")}
    for index, block in enumerate(_blocks(doc, "python")):
        try:
            exec(compile(block, f"{doc.name}[python #{index}]", "exec"), namespace)
        except Exception as exc:  # pragma: no cover - failure reporting
            pytest.fail(f"{doc.name} python block #{index} failed: {exc}\n---\n{block}")


@pytest.mark.parametrize("doc", _docs_with("cypher"), ids=lambda p: str(p.relative_to(DOCS)))
def test_cypher_snippets_execute(doc: Path, tmp_path) -> None:
    target = str(tmp_path / "docs.lbug")
    document = (DOCS / "family.owlxml").read_text(encoding="utf-8")
    Ontology.from_owlxml(document).save_projection(target).close()
    with WritableProjection.open(target) as projection:
        for index, block in enumerate(_blocks(doc, "cypher")):
            for statement in filter(None, (s.strip() for s in block.split(";"))):
                parameters = {
                    name: value
                    for name, value in _PARAMETER_VALUES.items()
                    if f"${name}" in statement
                } or None
                try:
                    projection.execute(statement, parameters=parameters)
                except Exception as exc:  # pragma: no cover - failure reporting
                    pytest.fail(f"{doc.name} cypher block #{index} failed: {exc}\n---\n{statement}")
