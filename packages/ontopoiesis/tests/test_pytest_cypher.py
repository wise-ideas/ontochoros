from __future__ import annotations

from pathlib import Path

import pytest

pytest_plugins = ("pytester",)


def test_plugin_collects_cypher_files_and_reports_violations(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytester.makefile(
        ".cypher",
        test_ok="MATCH (n) WHERE false RETURN n.uid",
        test_fail="MATCH (n) RETURN n.uid AS uid",
        helper="MATCH (n) RETURN n.uid",
        warn_quality="MATCH (n) RETURN n.uid AS uid",
    )
    graph_path = pytester.path / "ontology.lbug"
    graph_path.write_text("stub")

    class FakeProjection:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def execute(self, query: str, parameters=None) -> list[dict[str, object]]:
            if "WHERE false" in query:
                return []
            return [{"uid": "broken"}]

    monkeypatch.setattr(
        "ontopoiesis.cypher_test.plugin.open_cypher_runtime",
        lambda *args, **kwargs: FakeProjection(),
    )

    result = pytester.runpytest(
        str(pytester.path),
        "-p",
        "ontopoiesis.cypher_test.plugin",
        "--ontology",
        str(graph_path),
    )

    result.assert_outcomes(passed=2, failed=1)
    stdout = result.stdout.str()
    assert "test_ok.cypher" in stdout
    assert "test_fail.cypher" in stdout
    assert "helper.cypher" not in stdout
    assert "warn_quality.cypher" in stdout
    assert "query returned 1 violation row(s)" in stdout


def test_plugin_collects_warning_files_without_failing_run(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytester.makefile(
        ".cypher",
        warn_quality="MATCH (n) RETURN n.uid AS uid",
        test_ok="MATCH (n) WHERE false RETURN n.uid",
    )
    graph_path = pytester.path / "ontology.lbug"
    graph_path.write_text("stub")

    class FakeProjection:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def execute(self, query: str, parameters=None) -> list[dict[str, object]]:
            if "WHERE false" in query:
                return []
            return [{"uid": "warned"}]

    monkeypatch.setattr(
        "ontopoiesis.cypher_test.plugin.open_cypher_runtime",
        lambda *args, **kwargs: FakeProjection(),
    )

    result = pytester.runpytest(
        str(pytester.path),
        "-p",
        "ontopoiesis.cypher_test.plugin",
        "--ontology",
        str(graph_path),
    )

    result.assert_outcomes(passed=2)
    stdout = result.stdout.str()
    assert "cypher warnings" in stdout
    assert "WARN warn_quality.cypher" in stdout
    assert "warned" not in stdout


def test_plugin_explicit_warning_file_target_is_collected(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    query_path = pytester.path / "check_quality_warn.cypher"
    query_path.write_text("MATCH (n) RETURN n.uid AS uid")
    graph_path = pytester.path / "ontology.lbug"
    graph_path.write_text("stub")

    class FakeProjection:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def execute(self, query: str, parameters=None) -> list[dict[str, object]]:
            return [{"uid": "warned"}]

    monkeypatch.setattr(
        "ontopoiesis.cypher_test.plugin.open_cypher_runtime",
        lambda *args, **kwargs: FakeProjection(),
    )

    result = pytester.runpytest(
        str(query_path),
        "-p",
        "ontopoiesis.cypher_test.plugin",
        "--ontology",
        str(graph_path),
    )

    result.assert_outcomes(passed=1)
    assert "WARN check_quality_warn.cypher" in result.stdout.str()


def test_plugin_opens_lbug_inputs_directly(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytester.makefile(".cypher", test_ok="MATCH (n) WHERE false RETURN n.uid")
    graph_path = pytester.path / "ontology.lbug"
    graph_path.write_text("stub")
    seen: dict[str, Path] = {}

    class FakeProjection:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def execute(self, query: str, parameters=None) -> list[dict[str, object]]:
            return []

    def fake_open_cypher_runtime(path: Path, **_: object) -> FakeProjection:
        seen["path"] = path
        return FakeProjection()

    monkeypatch.setattr(
        "ontopoiesis.cypher_test.plugin.open_cypher_runtime", fake_open_cypher_runtime
    )

    result = pytester.runpytest(
        str(pytester.path),
        "-p",
        "ontopoiesis.cypher_test.plugin",
        "--ontology",
        str(graph_path),
    )

    result.assert_outcomes(passed=1)
    assert seen["path"] == graph_path


def test_plugin_collects_explicit_single_file_targets(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    query_path = pytester.path / "quality-rule.cypher"
    query_path.write_text("MATCH (n) WHERE false RETURN n.uid")
    graph_path = pytester.path / "ontology.lbug"
    graph_path.write_text("stub")

    class FakeProjection:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def execute(self, query: str, parameters=None) -> list[dict[str, object]]:
            return []

    monkeypatch.setattr(
        "ontopoiesis.cypher_test.plugin.open_cypher_runtime",
        lambda *args, **kwargs: FakeProjection(),
    )

    result = pytester.runpytest(
        str(query_path),
        "-p",
        "ontopoiesis.cypher_test.plugin",
        "--ontology",
        str(graph_path),
    )

    result.assert_outcomes(passed=1)


def test_plugin_reports_runtime_validation_errors_as_usage_errors(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytester.makefile(".cypher", test_fail="MATCH (n) RETURN n.uid AS uid")
    bad_path = pytester.path / "ontology.ttl"
    bad_path.write_text("stub")
    monkeypatch.setattr(
        "ontopoiesis.cypher_test.plugin.open_cypher_runtime",
        lambda _path: (_ for _ in ()).throw(ValueError("bad runtime input")),
    )

    result = pytester.runpytest(
        str(pytester.path),
        "-p",
        "ontopoiesis.cypher_test.plugin",
        "--ontology",
        str(bad_path),
    )

    assert result.ret == 2
    assert "bad runtime input" in result.stdout.str()


def test_plugin_requires_ontology_even_when_no_cypher_tests(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        test_plain="""
        def test_plain():
            assert True
        """
    )

    result = pytester.runpytest(str(pytester.path), "-p", "ontopoiesis.cypher_test.plugin")

    assert result.ret == 2
    assert "--ontology is required for cypher tests" in result.stdout.str()
