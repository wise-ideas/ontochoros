"""CLI command tests.

Commands run against real projections built from real OWL/XML: these tests
prove observable behavior (exit codes, files written, output content), not
argument passthrough. Mocks appear only at true process boundaries — the
in-process pytest.main invocation of the `test` command — and for
option-validation paths that never reach a projection.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from ontoplexis import Projection
from typer.testing import CliRunner

from ontopoiesis.app import app
from tests.conftest import WriteLbug

_PIZZA_OWX = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          ontologyIRI="https://example.org/pizza#">
  <Declaration><Class IRI="https://example.org/pizza#Pizza"/></Declaration>
  <SubClassOf>
    <Class IRI="https://example.org/pizza#Pizza"/>
    <Class IRI="https://example.org/pizza#Food"/>
  </SubClassOf>
</Ontology>
"""

_PIZZA_IRI = "https://example.org/pizza#Pizza"
_FOOD_IRI = "https://example.org/pizza#Food"


@pytest.fixture
def runner(monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    monkeypatch.setattr("ontopoiesis.app.dotenv.load_dotenv", lambda: None)
    # Typer force-enables rich terminal output when GITHUB_ACTIONS is set,
    # which injects ANSI codes into the output these tests assert on.
    monkeypatch.setattr("typer.rich_utils.FORCE_TERMINAL", False)
    return CliRunner()


def _invoke(runner: CliRunner, *args: str):
    return runner.invoke(app, list(args))


@pytest.fixture
def pizza_lbug(tmp_path: Path, write_lbug: WriteLbug) -> Path:
    return write_lbug(tmp_path / "pizza.lbug", _PIZZA_OWX)


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
    assert _PIZZA_IRI in document


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


def test_diff_cli_reports_changes_and_writes_json_output(
    runner: CliRunner, tmp_path: Path, write_lbug: WriteLbug
) -> None:
    before_path = write_lbug(tmp_path / "before.lbug", _PIZZA_OWX)
    after_path = write_lbug(tmp_path / "after.lbug", _PIZZA_OWX.replace("pizza#Food", "pizza#Meal"))
    output_path = tmp_path / "diff.json"

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
    rows = json.loads(output_path.read_text())
    assert sorted((row["status"], row["kind"]) for row in rows) == [
        ("added", "SubClassOf"),
        ("removed", "SubClassOf"),
    ]


def test_diff_cli_writes_table_output_to_file(
    runner: CliRunner, tmp_path: Path, write_lbug: WriteLbug
) -> None:
    before_path = write_lbug(tmp_path / "before.lbug", _PIZZA_OWX)
    after_path = write_lbug(tmp_path / "after.lbug", _PIZZA_OWX.replace("pizza#Food", "pizza#Meal"))
    output_path = tmp_path / "diff.tsv"

    result = _invoke(
        runner, "diff", str(before_path), str(after_path), "--output", str(output_path)
    )

    assert result.exit_code == 1
    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert lines[0].split("\t") == [
        "status",
        "kind",
        "iri",
        "count",
        "fingerprint",
        "ontology_iri",
    ]
    assert sorted(line.split("\t")[:2] for line in lines[1:]) == [
        ["added", "SubClassOf"],
        ["removed", "SubClassOf"],
    ]


def test_diff_cli_exits_zero_when_no_differences_found(
    runner: CliRunner, tmp_path: Path, write_lbug: WriteLbug
) -> None:
    before_path = write_lbug(tmp_path / "before.lbug", _PIZZA_OWX)
    after_path = write_lbug(tmp_path / "after.lbug", _PIZZA_OWX)

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


def test_impact_upstream_cli_lists_referencing_constructs(
    runner: CliRunner, pizza_lbug: Path
) -> None:
    result = _invoke(runner, "impact", "upstream", str(pizza_lbug), "--iri", _PIZZA_IRI)

    assert result.exit_code == 0
    assert "Declaration" in result.output
    assert "SubClassOf" in result.output
    assert "Ontology" in result.output


def test_impact_downstream_cli_reports_missing_rows_for_leaf_entity(
    runner: CliRunner, pizza_lbug: Path
) -> None:
    result = _invoke(runner, "impact", "downstream", str(pizza_lbug), "--iri", _PIZZA_IRI)

    assert result.exit_code == 0
    assert f"No constructs found for iri {_PIZZA_IRI}." in result.output


def test_impact_downstream_cli_accepts_uid(runner: CliRunner, pizza_lbug: Path) -> None:
    with Projection.open(pizza_lbug) as projection:
        (row,) = projection.execute("MATCH (n:N {kind: 'SubClassOf'}) RETURN n.uid AS uid")
    subclass_uid = str(row["uid"])

    result = _invoke(runner, "impact", "downstream", str(pizza_lbug), "--uid", subclass_uid)

    assert result.exit_code == 0
    assert _PIZZA_IRI in result.output
    assert _FOOD_IRI in result.output


def test_impact_upstream_cli_reports_nothing_for_unknown_seed(
    runner: CliRunner, pizza_lbug: Path
) -> None:
    result = _invoke(
        runner, "impact", "upstream", str(pizza_lbug), "--iri", "https://example.org/pizza#Nope"
    )

    assert result.exit_code == 0
    assert "No constructs found" in result.output


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
        _PIZZA_IRI,
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


def test_lint_cli_exits_zero_on_clean_projection(runner: CliRunner, pizza_lbug: Path) -> None:
    result = _invoke(runner, "lint", str(pizza_lbug))

    assert result.exit_code == 0
    assert "No lint violations found." in result.output


def test_lint_cli_exits_one_and_names_the_failing_rule(
    runner: CliRunner, tmp_path: Path, write_lbug: WriteLbug
) -> None:
    unsatisfiable = _PIZZA_OWX.replace(
        "https://example.org/pizza#Food", "http://www.w3.org/2002/07/owl#Nothing"
    )
    input_path = write_lbug(tmp_path / "broken.lbug", unsatisfiable)

    result = _invoke(runner, "lint", str(input_path))

    assert result.exit_code == 1
    assert "FAIL test_subclass_nothing.cypher" in result.output


def test_lint_cli_select_narrows_the_rule_set(
    runner: CliRunner, tmp_path: Path, write_lbug: WriteLbug
) -> None:
    # The same broken projection passes when only an unrelated rule runs.
    unsatisfiable = _PIZZA_OWX.replace(
        "https://example.org/pizza#Food", "http://www.w3.org/2002/07/owl#Nothing"
    )
    input_path = write_lbug(tmp_path / "broken.lbug", unsatisfiable)

    result = _invoke(runner, "lint", str(input_path), "--select", "E102")

    assert result.exit_code == 0


def test_lint_cli_rejects_non_lbug_input(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "ontology.ttl"
    input_path.write_text("ontology")

    result = _invoke(runner, "lint", str(input_path))

    assert result.exit_code == 2
    assert "input_path must point to a .lbug graph database" in result.output


def test_lint_cli_surfaces_selection_errors_as_bad_parameters(
    runner: CliRunner, pizza_lbug: Path
) -> None:
    result = _invoke(runner, "lint", str(pizza_lbug), "--select", "Z999")

    assert result.exit_code == 2
    assert "Unknown lint selector" in result.output


def test_lint_cli_warns_when_projection_contains_unresolved_imports(
    runner: CliRunner, tmp_path: Path, write_lbug: WriteLbug
) -> None:
    input_path = write_lbug(tmp_path / "importing.lbug", _IMPORTING_OWX)

    result = _invoke(runner, "lint", str(input_path), "--select", "D101")

    assert result.exit_code == 1
    assert "WARN import closure is unresolved" in result.output
    assert "contains 1 Import declaration" in result.output
    assert "ontopoiesis resolve" in result.output


# ---------------------------------------------------------------------------
# migrate
# ---------------------------------------------------------------------------

_EXAMPLE_MIGRATIONS = Path(__file__).resolve().parents[1] / "examples" / "migrations"


def _node_count(path: Path) -> int:
    with Projection.open(path) as projection:
        return projection.node_count


def test_migrate_cli_applies_migrations_and_writes_projection(
    runner: CliRunner, tmp_path: Path
) -> None:
    output_path = tmp_path / "migrated.lbug"

    result = _invoke(runner, "migrate", str(_EXAMPLE_MIGRATIONS), "--output", str(output_path))

    assert result.exit_code == 0
    assert output_path.exists()
    assert _node_count(output_path) > 0


def test_migrate_cli_uses_default_lbug_output_path(runner: CliRunner, tmp_path: Path) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "V0001__ontology.cypher").write_text(
        "MERGE (n:N {uid: '0x01', kind: 'Ontology'});"
    )

    result = _invoke(runner, "migrate", str(migrations_dir))

    assert result.exit_code == 0
    assert _node_count(tmp_path / "migrations.lbug") == 1


def test_migrate_cli_rejects_non_lbug_output_extension(runner: CliRunner, tmp_path: Path) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()

    result = _invoke(
        runner, "migrate", str(migrations_dir), "--output", str(tmp_path / "graph.out")
    )

    assert result.exit_code == 2
    assert "output_path must use a .lbug file extension" in result.output


def test_migrate_cli_resumes_existing_projection_without_reapplying(
    runner: CliRunner, tmp_path: Path
) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "V0001__ontology.cypher").write_text(
        "MERGE (n:N {uid: '0x01', kind: 'Ontology'});"
    )
    output_path = tmp_path / "graph.lbug"
    assert (
        _invoke(runner, "migrate", str(migrations_dir), "--output", str(output_path)).exit_code == 0
    )
    (migrations_dir / "V0002__more.cypher").write_text(
        "MERGE (n:N {uid: '0x02', kind: 'Ontology'});"
    )

    result = _invoke(runner, "migrate", str(migrations_dir), "--output", str(output_path))

    # V0001 is recorded as applied in the resumed projection; only V0002 runs.
    assert result.exit_code == 0
    assert _node_count(output_path) == 2


def test_migrate_cli_force_rebuilds_existing_output(runner: CliRunner, tmp_path: Path) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "V0001__ontology.cypher").write_text(
        "MERGE (n:N {uid: '0x01', kind: 'Ontology'});"
    )
    output_path = tmp_path / "graph.lbug"
    output_path.write_text("not a database")

    result = _invoke(
        runner, "migrate", str(migrations_dir), "--output", str(output_path), "--force"
    )

    assert result.exit_code == 0
    assert _node_count(output_path) == 1


# ---------------------------------------------------------------------------
# query
# ---------------------------------------------------------------------------


def test_query_cli_executes_cypher_and_prints_rows(runner: CliRunner, pizza_lbug: Path) -> None:
    result = _invoke(
        runner,
        "query",
        str(pizza_lbug),
        "--query",
        "MATCH (n:N {kind: 'Class'}) WHERE n.iri IS NOT NULL RETURN n.iri AS iri ORDER BY iri",
    )

    assert result.exit_code == 0
    assert _FOOD_IRI in result.output
    assert _PIZZA_IRI in result.output


def test_query_cli_prints_nothing_for_empty_result(runner: CliRunner, pizza_lbug: Path) -> None:
    result = _invoke(
        runner,
        "query",
        str(pizza_lbug),
        "--query",
        "MATCH (n:N {kind: 'Nope'}) RETURN n.uid AS uid",
    )

    assert result.exit_code == 0
    assert result.output.strip() == ""


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------


def test_render_cli_infers_format_from_output_path_and_writes_artifact(
    runner: CliRunner, pizza_lbug: Path, tmp_path: Path
) -> None:
    output_path = tmp_path / "graph.dot"

    result = _invoke(
        runner,
        "render",
        str(pizza_lbug),
        _PIZZA_IRI,
        "https://example.org/pizza#Missing",
        "--output",
        str(output_path),
        "--include-external",
    )

    assert result.exit_code == 0
    assert output_path.read_text(encoding="utf-8").startswith("digraph")
    assert "IRI not found in projection: https://example.org/pizza#Missing" in result.output


def test_render_cli_writes_svg_without_graphviz(
    runner: CliRunner, pizza_lbug: Path, tmp_path: Path
) -> None:
    output_path = tmp_path / "graph.svg"

    result = _invoke(runner, "render", str(pizza_lbug), "--output", str(output_path))

    assert result.exit_code == 0
    assert output_path.read_text(encoding="utf-8").startswith("<svg")


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
    # pytest.main is a process boundary: invoking a second in-process pytest
    # session inside this one is unsupported, so the handoff stays mocked.
    # The plugin behind it is tested for real in test_pytest_cypher.py.
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

    result = _invoke(runner, "test", str(input_path), str(tests_dir))

    assert result.exit_code == 0
    assert seen["args"] == ["--ontology", str(input_path), str(tests_dir)]
    assert len(seen["plugins"]) == 1


def test_test_cli_exits_two_when_no_tests_are_found(runner: CliRunner, tmp_path: Path) -> None:
    input_path = tmp_path / "graph.lbug"
    tests_dir = tmp_path / "tests"
    input_path.write_text("graph")
    tests_dir.mkdir()

    result = _invoke(runner, "test", str(input_path), str(tests_dir))

    assert result.exit_code == 2
    assert "No test_*.cypher, *_test.cypher, warn_*.cypher, or *_warn.cypher files found" in (
        result.output
    )


def test_storage_backend_is_never_imported_directly() -> None:
    """`real_ladybug` is ontoplexis's private storage dependency.

    Ontopoiesis reaches storage only through ontoplexis `Projection` handles;
    importing the backend here would leak the seam across the package boundary.
    """
    import ontopoiesis

    src = Path(ontopoiesis.__file__).parent
    offenders = [
        str(path.relative_to(src))
        for path in src.rglob("*.py")
        if "real_ladybug" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []


# ---------------------------------------------------------------------------
# convert / resolve / reason (the opt-in ROBOT shim)
# ---------------------------------------------------------------------------

_ROBOT_JAR = Path(__file__).resolve().parents[2] / "ontoplexis" / ".cache" / "robot" / "robot.jar"

_needs_robot = pytest.mark.skipif(
    not _ROBOT_JAR.is_file(), reason="ROBOT jar not fetched (make fetch-robot)"
)

_MINI_TTL = """\
@prefix : <http://example.org/z#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<http://example.org/z> rdf:type owl:Ontology .
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:C rdf:type owl:Class .
:A rdfs:subClassOf :B .
:B rdfs:subClassOf :C .
"""

_IMPORTING_OWX = """\
<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          ontologyIRI="https://example.org/root">
  <Import>https://example.org/imported</Import>
  <Declaration><Class IRI="https://example.org/root#A"/></Declaration>
  <SubClassOf>
    <Class IRI="https://example.org/root#A"/>
    <Class IRI="https://example.org/imported#B"/>
  </SubClassOf>
</Ontology>
"""

_IMPORTED_OWX = """\
<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          ontologyIRI="https://example.org/imported">
  <Declaration><Class IRI="https://example.org/imported#B"/></Declaration>
</Ontology>
"""


def test_convert_cli_fails_clearly_without_jar(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("ROBOT_JAR", raising=False)
    source = tmp_path / "mini.ttl"
    source.write_text(_MINI_TTL, encoding="utf-8")

    result = _invoke(runner, "convert", str(source))

    assert result.exit_code != 0
    assert "ROBOT_JAR" in result.output


def test_reason_cli_fails_clearly_on_missing_jar_path(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ROBOT_JAR", str(tmp_path / "nowhere.jar"))
    source = tmp_path / "mini.owx"
    source.write_text("<Ontology/>", encoding="utf-8")

    result = _invoke(runner, "reason", str(source))

    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_convert_cli_rejects_existing_output_before_needing_the_jar(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("ROBOT_JAR", raising=False)
    source = tmp_path / "mini.ttl"
    source.write_text(_MINI_TTL, encoding="utf-8")
    (tmp_path / "mini.owx").write_text("occupied", encoding="utf-8")

    result = _invoke(runner, "convert", str(source))

    assert result.exit_code != 0
    assert "--force" in result.output


def test_resolve_cli_rejects_existing_output_before_needing_the_jar(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("ROBOT_JAR", raising=False)
    source = tmp_path / "root.owx"
    source.write_text(_IMPORTING_OWX, encoding="utf-8")
    (tmp_path / "root.closure.owx").write_text("occupied", encoding="utf-8")

    result = _invoke(runner, "resolve", str(source))

    assert result.exit_code != 0
    assert "--force" in result.output


@_needs_robot
def test_resolve_build_lint_pipeline_uses_catalogued_import_closure(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ROBOT_JAR", str(_ROBOT_JAR))
    source = tmp_path / "root.owx"
    imported = tmp_path / "imported.owx"
    catalog = tmp_path / "catalog.xml"
    source.write_text(_IMPORTING_OWX, encoding="utf-8")
    imported.write_text(_IMPORTED_OWX, encoding="utf-8")
    catalog.write_text(
        '<?xml version="1.0"?>\n'
        '<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">\n'
        f'  <uri name="https://example.org/imported" uri="{imported.as_uri()}"/>\n'
        "</catalog>\n",
        encoding="utf-8",
    )

    resolved = _invoke(runner, "resolve", str(source), "--catalog", str(catalog))

    assert resolved.exit_code == 0
    closure = tmp_path / "root.closure.owx"
    document = closure.read_text(encoding="utf-8")
    assert "https://example.org/imported#B" in document
    assert "<Import>" not in document
    assert _invoke(runner, "build", str(closure)).exit_code == 0
    linted = _invoke(
        runner,
        "lint",
        str(tmp_path / "root.closure.lbug"),
        "--select",
        "D101",
    )
    assert linted.exit_code == 0
    assert "No lint violations found." in linted.output


@_needs_robot
def test_convert_reason_build_pipeline_materializes_inferences(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ROBOT_JAR", str(_ROBOT_JAR))
    source = tmp_path / "mini.ttl"
    source.write_text(_MINI_TTL, encoding="utf-8")

    assert _invoke(runner, "convert", str(source)).exit_code == 0
    converted = tmp_path / "mini.owx"
    assert _invoke(runner, "reason", str(converted), "--include-indirect").exit_code == 0
    reasoned = tmp_path / "mini.reasoned.owx"
    # Provenance: inferred axioms are annotated by default.
    assert "is_inferred" in reasoned.read_text(encoding="utf-8")
    assert _invoke(runner, "build", str(reasoned)).exit_code == 0

    with Projection.open(tmp_path / "mini.reasoned.lbug") as projection:
        rows = projection.execute(
            "MATCH (a:N)-[:D {relation:'subclass_of'}]->(b:N) "
            "RETURN a.iri AS sub, b.iri AS super ORDER BY sub, super"
        )
    pairs = {(row["sub"], row["super"]) for row in rows}
    # Told: A⊑B, B⊑C. Materialized by ELK with --include-indirect: A⊑C —
    # one hop like any told axiom.
    assert ("http://example.org/z#A", "http://example.org/z#C") in pairs
