from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ontopoiesis.app import app
from ontopoiesis.commands.impact import (
    _ImpactDirection as ImpactDirection,
)
from ontopoiesis.commands.impact import (
    _ImpactSeedKind as ImpactSeedKind,
)
from ontopoiesis.diff_projection import DiffRow
from ontopoiesis.lint import LintResults, LintRuleSelectionError, LintViolation
from ontopoiesis.migrations import MigrationRecord, MigrationResult
from ontopoiesis.render import RenderFormat
from ontopoiesis.render import RenderResult as RenderArtifact

_PIZZA_OWX = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          ontologyIRI="https://example.org/pizza#">
  <SubClassOf>
    <Class IRI="https://example.org/pizza#Pizza"/>
    <Class IRI="https://example.org/pizza#Food"/>
  </SubClassOf>
</Ontology>
"""


@pytest.fixture
def runner(monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    monkeypatch.setattr("ontopoiesis.app.dotenv.load_dotenv", lambda: None)
    return CliRunner()


def _invoke(runner: CliRunner, *args: str):
    return runner.invoke(app, list(args))


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


def test_build_cli_builds_projection_from_owlxml(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "ontology.owx"
    input_path.write_text(_PIZZA_OWX)

    result = _invoke(runner, "build", str(input_path))

    assert result.exit_code == 0
    assert (tmp_path / "ontology.lbug").exists()


def test_build_cli_rejects_non_lbug_output_extension(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "ontology.owx"
    input_path.write_text(_PIZZA_OWX)

    result = _invoke(runner, "build", str(input_path), "--output", str(tmp_path / "graph.sqlite"))

    assert result.exit_code == 2
    assert "output_path must use a .lbug file extension" in result.output


def test_build_cli_rejects_existing_output_without_force(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "ontology.owx"
    input_path.write_text(_PIZZA_OWX)
    output_path = tmp_path / "ontology.lbug"
    output_path.write_text("original")

    result = _invoke(runner, "build", str(input_path))

    assert result.exit_code == 2
    assert "output_path already exists" in result.output
    assert output_path.read_text() == "original"


def test_build_cli_rejects_malformed_xml(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "ontology.ttl"
    input_path.write_text("@prefix ex: <https://example.org#> .")

    result = _invoke(runner, "build", str(input_path))

    assert result.exit_code == 2
    assert "well-formed XML" in result.output


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------


def test_export_cli_round_trips_projection_to_owlxml(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "ontology.owx"
    input_path.write_text(_PIZZA_OWX)
    build_result = _invoke(runner, "build", str(input_path))
    assert build_result.exit_code == 0

    exported_path = tmp_path / "exported.owx"
    result = _invoke(
        runner, "export", str(tmp_path / "ontology.lbug"), "--output", str(exported_path)
    )

    assert result.exit_code == 0
    document = exported_path.read_text(encoding="utf-8")
    assert "SubClassOf" in document
    assert "https://example.org/pizza#Pizza" in document


def test_export_cli_defaults_output_to_owx_beside_input(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "ontology.owx"
    input_path.write_text(_PIZZA_OWX)
    assert _invoke(runner, "build", str(input_path)).exit_code == 0
    input_path.unlink()

    result = _invoke(runner, "export", str(tmp_path / "ontology.lbug"))

    assert result.exit_code == 0
    assert (tmp_path / "ontology.owx").exists()


def test_export_cli_rejects_non_lbug_input(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "ontology.owx"
    input_path.write_text(_PIZZA_OWX)

    result = _invoke(runner, "export", str(input_path))

    assert result.exit_code == 2
    assert "input_path must point to a .lbug graph database" in result.output


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------


def test_diff_cli_writes_json_output(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    before_path = tmp_path / "before.lbug"
    after_path = tmp_path / "after.lbug"
    output_path = tmp_path / "diff.json"
    before_path.write_text("before")
    after_path.write_text("after")

    monkeypatch.setattr(
        "ontopoiesis.commands.diff.diff_projections",
        lambda *_args: [
            DiffRow(
                status="added",
                kind="Class",
                iri="https://example.org/A",
                count=1,
                fingerprint="abc",
            )
        ],
    )

    result = _invoke(
        runner,
        "diff",
        str(before_path),
        str(after_path),
        "--format",
        "json",
        "--output",
        str(output_path),
    )

    assert result.exit_code == 1
    assert '"status": "added"' in output_path.read_text()


def test_diff_cli_exits_zero_when_no_differences_found(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    before_path = tmp_path / "before.lbug"
    after_path = tmp_path / "after.lbug"
    before_path.write_text("before")
    after_path.write_text("after")

    monkeypatch.setattr("ontopoiesis.commands.diff.diff_projections", lambda *_args: [])

    result = _invoke(runner, "diff", str(before_path), str(after_path))

    assert result.exit_code == 0
    assert "No differences found." in result.output


def test_diff_cli_rejects_unknown_output_format(runner: CliRunner, tmp_path: Path) -> None:
    before_path = tmp_path / "before.lbug"
    after_path = tmp_path / "after.lbug"
    before_path.write_text("before")
    after_path.write_text("after")

    result = _invoke(runner, "diff", str(before_path), str(after_path), "--format", "yaml")

    assert result.exit_code == 2
    assert "output_format must be one of: table, json" in result.output


# ---------------------------------------------------------------------------
# impact
# ---------------------------------------------------------------------------


def test_impact_upstream_cli_passes_direction_and_rows(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "graph.lbug"
    input_path.write_text("graph")
    seen: dict[str, object] = {}

    def fake_query(
        path: Path,
        seed: str,
        *,
        seed_kind: ImpactSeedKind,
        direction: ImpactDirection,
    ) -> list[dict[str, object]]:
        seen["path"] = path
        seen["seed"] = seed
        seen["seed_kind"] = seed_kind
        seen["direction"] = direction
        return [{"uid": "0x1", "kind": "Class", "depth": 0, "iri": seed}]

    monkeypatch.setattr("ontopoiesis.commands.impact._query_impact", fake_query)
    monkeypatch.setattr(
        "ontopoiesis.commands.impact.print_query_table",
        lambda rows: seen.setdefault("rows", list(rows)),
    )

    result = _invoke(
        runner, "impact", "upstream", str(input_path), "--iri", "https://example.org/A"
    )

    assert result.exit_code == 0
    assert seen["path"] == input_path
    assert seen["seed"] == "https://example.org/A"
    assert seen["seed_kind"] == ImpactSeedKind.IRI
    assert seen["direction"] == ImpactDirection.UPSTREAM
    assert seen["rows"] == [
        {"uid": "0x1", "kind": "Class", "depth": 0, "iri": "https://example.org/A"}
    ]


def test_impact_downstream_cli_reports_missing_rows(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "graph.lbug"
    input_path.write_text("graph")
    notices: list[tuple[str, bool]] = []

    monkeypatch.setattr("ontopoiesis.commands.impact._query_impact", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        "ontopoiesis.commands.impact.print_notice",
        lambda message, err=False: notices.append((message, err)),
    )

    result = _invoke(
        runner, "impact", "downstream", str(input_path), "--iri", "https://example.org/A"
    )

    assert result.exit_code == 0
    assert notices == [("No constructs found for iri https://example.org/A.", False)]


def test_impact_downstream_cli_accepts_uid(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "graph.lbug"
    input_path.write_text("graph")
    seen: dict[str, object] = {}

    def fake_query(
        path: Path,
        seed: str,
        *,
        seed_kind: ImpactSeedKind,
        direction: ImpactDirection,
    ) -> list[dict[str, object]]:
        seen["path"] = path
        seen["seed"] = seed
        seen["seed_kind"] = seed_kind
        seen["direction"] = direction
        return [{"uid": "0x2", "kind": "SubClassOf", "depth": 1, "iri": None}]

    monkeypatch.setattr("ontopoiesis.commands.impact._query_impact", fake_query)
    monkeypatch.setattr(
        "ontopoiesis.commands.impact.print_query_table",
        lambda rows: seen.setdefault("rows", list(rows)),
    )

    result = _invoke(runner, "impact", "downstream", str(input_path), "--uid", "0x1")

    assert result.exit_code == 0
    assert seen["path"] == input_path
    assert seen["seed"] == "0x1"
    assert seen["seed_kind"] == ImpactSeedKind.UID
    assert seen["direction"] == ImpactDirection.DOWNSTREAM
    assert seen["rows"] == [{"uid": "0x2", "kind": "SubClassOf", "depth": 1, "iri": None}]


def test_impact_cli_requires_exactly_one_seed_flag(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "graph.lbug"
    input_path.write_text("graph")

    missing = _invoke(runner, "impact", "upstream", str(input_path))
    both = _invoke(
        runner,
        "impact",
        "upstream",
        str(input_path),
        "--iri",
        "https://example.org/A",
        "--uid",
        "0x1",
    )

    assert missing.exit_code == 2
    assert both.exit_code == 2
    assert "Pass exactly one of --iri or --uid." in missing.output
    assert "Pass exactly one of --iri or --uid." in both.output


# ---------------------------------------------------------------------------
# lint
# ---------------------------------------------------------------------------


def test_lint_cli_exits_zero_and_passes_selection_options(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "ontology.lbug"
    input_path.write_text("graph")
    seen: dict[str, object] = {}

    def fake_resolve_lint_rule_selection(**kwargs: object) -> list[str]:
        seen["selection"] = kwargs
        return ["RULE001"]

    def fake_run_lint_on_path(path: Path, *, rules: list[str]) -> LintResults:
        seen["path"] = path
        seen["rules"] = rules
        return LintResults()

    monkeypatch.setattr(
        "ontopoiesis.commands.lint_command.resolve_lint_rule_selection",
        fake_resolve_lint_rule_selection,
    )
    monkeypatch.setattr("ontopoiesis.commands.lint_command.run_lint_on_path", fake_run_lint_on_path)
    monkeypatch.setattr(
        "ontopoiesis.commands.lint_command.print_notice", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        "ontopoiesis.commands.lint_command.print_summary", lambda *_args, **_kwargs: None
    )

    result = _invoke(
        runner,
        "lint",
        str(input_path),
        "--profile",
        "editorial",
        "--select",
        "RULE",
        "--extend-select",
        "WARN",
        "--ignore",
        "SKIP",
    )

    assert result.exit_code == 0
    assert seen["selection"] == {
        "profiles": ["editorial"],
        "select": ["RULE"],
        "extend_select": ["WARN"],
        "ignore": ["SKIP"],
    }
    assert seen["path"] == input_path
    assert seen["rules"] == ["RULE001"]


def test_lint_cli_exits_one_for_failures(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "ontology.lbug"
    input_path.write_text("graph")

    monkeypatch.setattr(
        "ontopoiesis.commands.lint_command.resolve_lint_rule_selection", lambda **_kwargs: []
    )
    monkeypatch.setattr(
        "ontopoiesis.commands.lint_command.run_lint_on_path",
        lambda *_args, **_kwargs: LintResults(
            violations=[
                LintViolation(
                    path=Path("rules/test.cypher"),
                    rows=[{"uid": "0x1"}],
                    is_warn=False,
                )
            ]
        ),
    )
    monkeypatch.setattr(
        "ontopoiesis.commands.lint_command.print_notice", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        "ontopoiesis.commands.lint_command.print_summary", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        "ontopoiesis.commands.lint_command.print_violation_rows", lambda *_args, **_kwargs: None
    )

    result = _invoke(runner, "lint", str(input_path))

    assert result.exit_code == 1


def test_lint_cli_rejects_non_lbug_input(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "ontology.ttl"
    input_path.write_text("ontology")

    result = _invoke(runner, "lint", str(input_path))

    assert result.exit_code == 2
    assert "input_path must point to a .lbug graph database" in result.output


def test_lint_cli_surfaces_selection_errors_as_bad_parameters(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "ontology.lbug"
    input_path.write_text("graph")

    monkeypatch.setattr(
        "ontopoiesis.commands.lint_command.resolve_lint_rule_selection",
        lambda **_kwargs: (_ for _ in ()).throw(LintRuleSelectionError("unknown selector")),
    )

    result = _invoke(runner, "lint", str(input_path))

    assert result.exit_code == 2
    assert "unknown selector" in result.output


# ---------------------------------------------------------------------------
# migrate
# ---------------------------------------------------------------------------


def test_migrate_cli_runs_and_writes_projection(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    output_path = tmp_path / "migrated.lbug"
    seen: dict[str, object] = {}

    class _Runner:
        def __init__(self, start_from: Path | None = None) -> None:
            seen["start_from"] = start_from

        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> None:
            seen["closed"] = True

        def apply_all(self, path: Path) -> MigrationResult:
            seen["migrations_dir"] = path
            return MigrationResult(
                applied=[
                    MigrationRecord(
                        migration_id="001_init",
                        path=migrations_dir / "001_init.cypher",
                    )
                ],
                node_count=3,
                edge_count=4,
            )

        @property
        def database_path(self) -> Path:
            return tmp_path / "temp.lbug"

        def build_database(self):
            seen["built_database"] = True

            class _Projection:
                def close(self) -> None:
                    seen["projection_closed"] = True

            (tmp_path / "temp.lbug").write_text("graph")
            return _Projection()

    monkeypatch.setattr("ontopoiesis.commands.migrate.MigrationRunner", _Runner)
    monkeypatch.setattr(
        "ontopoiesis.commands.migrate.print_path_action", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        "ontopoiesis.commands.migrate.print_summary", lambda *_args, **_kwargs: None
    )

    result = _invoke(
        runner,
        "migrate",
        str(migrations_dir),
        "--output",
        str(output_path),
    )

    assert result.exit_code == 0
    assert output_path.read_text() == "graph"
    assert seen == {
        "start_from": None,
        "migrations_dir": migrations_dir,
        "built_database": True,
        "projection_closed": True,
        "closed": True,
    }


def test_migrate_cli_uses_default_lbug_output_path(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    output_path = tmp_path / "migrations.lbug"
    seen: dict[str, object] = {}

    class _Runner:
        def __init__(self, start_from: Path | None = None) -> None:
            seen["start_from"] = start_from

        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def apply_all(self, path: Path) -> MigrationResult:
            seen["migrations_dir"] = path
            return MigrationResult(applied=[], node_count=0, edge_count=0)

        @property
        def database_path(self) -> Path:
            return tmp_path / "temp.lbug"

        def build_database(self):
            class _Projection:
                def close(self) -> None:
                    return None

            (tmp_path / "temp.lbug").write_text("graph")
            return _Projection()

    monkeypatch.setattr("ontopoiesis.commands.migrate.MigrationRunner", _Runner)
    monkeypatch.setattr(
        "ontopoiesis.commands.migrate.print_path_action", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        "ontopoiesis.commands.migrate.print_summary", lambda *_args, **_kwargs: None
    )

    result = _invoke(runner, "migrate", str(migrations_dir))

    assert result.exit_code == 0
    assert output_path.read_text() == "graph"
    assert seen == {
        "start_from": None,
        "migrations_dir": migrations_dir,
    }


def test_migrate_cli_rejects_non_lbug_output_extension(runner: CliRunner, tmp_path: Path) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()

    result = _invoke(
        runner, "migrate", str(migrations_dir), "--output", str(tmp_path / "graph.out")
    )

    assert result.exit_code == 2
    assert "output_path must use a .lbug file extension" in result.output


def test_migrate_cli_resumes_existing_projection(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    output_path = tmp_path / "graph.lbug"
    output_path.write_text("existing")
    seen: dict[str, object] = {}

    class _Runner:
        def __init__(self, start_from: Path | None = None) -> None:
            seen["start_from"] = start_from

        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def apply_all(self, path: Path) -> MigrationResult:
            seen["migrations_dir"] = path
            return MigrationResult(applied=[], node_count=3, edge_count=4)

    monkeypatch.setattr("ontopoiesis.commands.migrate.MigrationRunner", _Runner)
    monkeypatch.setattr(
        "ontopoiesis.commands.migrate.print_path_action", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        "ontopoiesis.commands.migrate.print_summary", lambda *_args, **_kwargs: None
    )

    result = _invoke(runner, "migrate", str(migrations_dir), "--output", str(output_path))

    assert result.exit_code == 0
    assert output_path.read_text() == "existing"
    assert seen == {
        "start_from": output_path,
        "migrations_dir": migrations_dir,
    }


def test_migrate_cli_force_rebuilds_existing_output(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    output_path = tmp_path / "graph.lbug"
    output_path.write_text("existing")
    seen: dict[str, object] = {}

    class _Runner:
        def __init__(self, start_from: Path | None = None) -> None:
            seen["start_from"] = start_from

        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def apply_all(self, path: Path) -> MigrationResult:
            seen["migrations_dir"] = path
            return MigrationResult(applied=[], node_count=1, edge_count=0)

        @property
        def database_path(self) -> Path:
            return tmp_path / "temp.lbug"

        def build_database(self):
            seen["built_database"] = True

            class _Projection:
                def close(self) -> None:
                    seen["projection_closed"] = True

            (tmp_path / "temp.lbug").write_text("rebuilt")
            return _Projection()

    monkeypatch.setattr("ontopoiesis.commands.migrate.MigrationRunner", _Runner)
    monkeypatch.setattr(
        "ontopoiesis.commands.migrate.print_path_action", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        "ontopoiesis.commands.migrate.print_summary", lambda *_args, **_kwargs: None
    )

    result = _invoke(
        runner, "migrate", str(migrations_dir), "--output", str(output_path), "--force"
    )

    assert result.exit_code == 0
    assert output_path.read_text() == "rebuilt"
    assert seen == {
        "start_from": None,
        "migrations_dir": migrations_dir,
        "built_database": True,
        "projection_closed": True,
    }


# ---------------------------------------------------------------------------
# query
# ---------------------------------------------------------------------------


def test_query_cli_executes_cypher_and_prints_rows(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "graph.lbug"
    input_path.write_text("graph")
    seen: dict[str, object] = {}

    class _Projection:
        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def execute(self, cypher: str):
            seen["cypher"] = cypher
            return [{"uid": "0x1", "kind": "Class"}]

    def fake_open_projection(path: Path) -> _Projection:
        seen["path"] = path
        return _Projection()

    monkeypatch.setattr("ontopoiesis.commands.query.Projection.open", fake_open_projection)
    monkeypatch.setattr(
        "ontopoiesis.commands.query.print_query_table",
        lambda rows: seen.setdefault("rows", list(rows)),
    )

    result = _invoke(runner, "query", str(input_path), "--query", "MATCH (n) RETURN n.uid AS uid")

    assert result.exit_code == 0
    assert seen["path"] == input_path
    assert seen["cypher"] == "MATCH (n) RETURN n.uid AS uid"
    assert seen["rows"] == [{"uid": "0x1", "kind": "Class"}]


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------


def test_render_cli_infers_format_from_output_path_and_writes_artifact(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "graph.lbug"
    output_path = tmp_path / "graph.dot"
    input_path.write_text("graph")
    seen: dict[str, object] = {}
    notices: list[tuple[str, bool]] = []

    def fake_render(
        path: Path,
        iris: list[str] | None,
        *,
        output_format: RenderFormat,
        include_external: bool,
    ):
        seen["path"] = path
        seen["iris"] = iris
        seen["output_format"] = output_format
        seen["include_external"] = include_external
        return RenderArtifact(
            format=RenderFormat.DOT,
            content="digraph {}",
            node_count=2,
            edge_count=1,
            missing_iris=["https://example.org/Missing"],
        )

    monkeypatch.setattr("ontopoiesis.commands.render_command.render_projection", fake_render)
    monkeypatch.setattr(
        "ontopoiesis.commands.render_command.print_notice",
        lambda message, err=False: notices.append((message, err)),
    )
    monkeypatch.setattr(
        "ontopoiesis.commands.render_command.print_path_action", lambda *_args: None
    )
    monkeypatch.setattr("ontopoiesis.commands.render_command.print_summary", lambda *_args: None)

    result = _invoke(
        runner,
        "render",
        str(input_path),
        "https://example.org/A",
        "--output",
        str(output_path),
        "--include-external",
    )

    assert result.exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "digraph {}"
    assert seen == {
        "path": input_path,
        "iris": ["https://example.org/A"],
        "output_format": RenderFormat.DOT,
        "include_external": True,
    }
    assert notices == [("IRI not found in projection: https://example.org/Missing", True)]


def test_render_cli_rejects_unsupported_format(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "graph.lbug"
    input_path.write_text("graph")

    result = _invoke(
        runner,
        "render",
        str(input_path),
        "--output",
        str(tmp_path / "graph.svg"),
        "--format",
        "pdf",
    )

    assert result.exit_code == 2
    assert "Invalid value for '--format'" in result.output
    assert "Unsupported format 'pdf'" in result.output


# ---------------------------------------------------------------------------
# test
# ---------------------------------------------------------------------------


def test_test_cli_invokes_pytest_with_resolved_test_paths(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "graph.lbug"
    tests_dir = tmp_path / "tests"
    input_path.write_text("graph")
    tests_dir.mkdir()
    seen: dict[str, object] = {}

    monkeypatch.setattr(
        "ontopoiesis.commands.test.resolve_cypher_tests",
        lambda paths: [tests_dir / "test_query.cypher"],
    )

    def fake_pytest_main(args: list[str], *, plugins: list[object]) -> int:
        seen["args"] = args
        seen["plugins"] = plugins
        return 0

    monkeypatch.setattr("ontopoiesis.commands.test.pytest.main", fake_pytest_main)

    result = _invoke(
        runner,
        "test",
        str(input_path),
        str(tests_dir),
    )

    assert result.exit_code == 0
    assert seen["args"] == [
        "--ontology",
        str(input_path),
        str(tests_dir),
    ]
    assert len(seen["plugins"]) == 1


def test_test_cli_exits_two_when_no_tests_are_found(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "graph.lbug"
    tests_dir = tmp_path / "tests"
    input_path.write_text("graph")
    tests_dir.mkdir()

    monkeypatch.setattr("ontopoiesis.commands.test.resolve_cypher_tests", lambda _paths: [])

    result = _invoke(runner, "test", str(input_path), str(tests_dir))

    assert result.exit_code == 2
    assert "No test_*.cypher, *_test.cypher, warn_*.cypher, or *_warn.cypher files found" in (
        result.output
    )
