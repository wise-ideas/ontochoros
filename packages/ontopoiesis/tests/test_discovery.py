"""Cypher test-file discovery: targets, patterns, and de-duplication."""

from __future__ import annotations

from pathlib import Path

from ontopoiesis.cypher_test.discovery import (
    is_warning_cypher_path,
    matches_cypher_pattern,
    resolve_cypher_target,
    resolve_cypher_tests,
)


def test_directory_targets_collect_only_pattern_matching_files(tmp_path: Path) -> None:
    (tmp_path / "test_a.cypher").write_text("RETURN 1;")
    (tmp_path / "b_test.cypher").write_text("RETURN 1;")
    (tmp_path / "warn_c.cypher").write_text("RETURN 1;")
    (tmp_path / "d_warn.cypher").write_text("RETURN 1;")
    (tmp_path / "helper.cypher").write_text("RETURN 1;")
    (tmp_path / "test_not_cypher.txt").write_text("nope")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "test_e.cypher").write_text("RETURN 1;")

    resolved = resolve_cypher_target(tmp_path)

    assert [path.relative_to(tmp_path) for path in resolved] == [
        Path("b_test.cypher"),
        Path("d_warn.cypher"),
        Path("nested/test_e.cypher"),
        Path("test_a.cypher"),
        Path("warn_c.cypher"),
    ]


def test_explicit_cypher_file_target_bypasses_the_name_patterns(tmp_path: Path) -> None:
    helper = tmp_path / "helper.cypher"
    helper.write_text("RETURN 1;")

    assert resolve_cypher_target(helper) == [helper]
    assert not matches_cypher_pattern(helper)


def test_missing_or_non_cypher_targets_resolve_to_nothing(tmp_path: Path) -> None:
    assert resolve_cypher_target(tmp_path / "absent") == []
    text_file = tmp_path / "notes.txt"
    text_file.write_text("nope")
    assert resolve_cypher_target(text_file) == []


def test_resolve_cypher_tests_deduplicates_overlapping_targets(tmp_path: Path) -> None:
    test_file = tmp_path / "test_a.cypher"
    test_file.write_text("RETURN 1;")

    resolved = resolve_cypher_tests([tmp_path, test_file, tmp_path])

    assert resolved == [test_file]


def test_resolve_cypher_tests_defaults_to_the_tests_directory(tmp_path: Path, monkeypatch) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    test_file = tests_dir / "test_a.cypher"
    test_file.write_text("RETURN 1;")
    monkeypatch.chdir(tmp_path)

    assert resolve_cypher_tests(None) == [Path("tests/test_a.cypher")]


def test_warning_paths_are_distinguished_from_error_paths() -> None:
    assert is_warning_cypher_path(Path("warn_free_floating.cypher"))
    assert is_warning_cypher_path(Path("orphans_warn.cypher"))
    assert not is_warning_cypher_path(Path("test_subclass.cypher"))
