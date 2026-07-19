"""Every corpus fixture must validate against the current construct models.

The ``fixtures/cases`` corpus (OWL 2 Primer and Structural Specification
examples, serialized by the OWLAPI-side record serializers) cannot currently
be regenerated — see TODO.md. That makes it a one-way ratchet: if a model
changes shape, this gate is what notices, because the fixtures cannot be
quietly re-emitted to match.

Cross-package coupling: the sibling ``.xml`` documents in the same directory
are consumed by ontoplexis (``tests/test_corpus_roundtrip.py``) via a
relative path into this package's test tree. Each ``.jsonl``/``.xml`` pair
renders the same example, so moving, renaming, or unpairing files here
breaks that suite too.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ontophora.envelope import records_from_jsonl, records_to_jsonl

CASES = Path(__file__).parent / "fixtures" / "cases"


def _corpus() -> list[Path]:
    cases = sorted(CASES.glob("*.jsonl"))
    if not cases:
        raise AssertionError(f"No corpus fixtures found under {CASES}")
    return cases


def test_corpus_cases_are_complete_jsonl_xml_pairs() -> None:
    # The corpus cannot be regenerated, so a half-deleted or half-added case
    # would silently thin one suite's coverage: every record file must have
    # its source document and vice versa.
    jsonl_stems = {path.stem for path in CASES.glob("*.jsonl")}
    xml_stems = {path.stem for path in CASES.glob("*.xml")}

    assert jsonl_stems == xml_stems
    assert jsonl_stems


@pytest.mark.parametrize("case", _corpus(), ids=lambda p: p.stem)
def test_corpus_fixture_validates_and_round_trips(case: Path) -> None:
    records = records_from_jsonl(case.read_text(encoding="utf-8"))

    assert records, f"{case.name} decoded to zero records"
    assert len({record.uid for record in records}) == len(records)
    # The envelope encoder accepts everything it decoded, and a second
    # decode is the identity: the corpus stays representable, not merely
    # parseable.
    assert records_from_jsonl(records_to_jsonl(records)) == records
