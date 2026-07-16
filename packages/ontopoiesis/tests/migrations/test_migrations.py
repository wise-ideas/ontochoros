from pathlib import Path

import pytest
from ontoplexis import ProjectionStorageError

from ontopoiesis.migrations import MigrationError, MigrationRunner, axiom_uid, scalar_uid
from ontopoiesis.migrations.uids import MIGRATION_UID_DIGEST_HEX_LENGTH


def test_migration_runner_executes_rendered_cypher_verbatim() -> None:
    migrations = Path(__file__).resolve().parents[2] / "examples" / "migrations"
    with MigrationRunner() as runner:
        result = runner.apply_all(migrations)

        assert [record.migration_id for record in result.applied] == [
            "V0001",
            "V0002",
            "V0003",
            "V0004",
        ]
        assert result.node_count > 0
        assert result.edge_count > 0

        graph = runner.graph()
        ontology_edges = [edge for edge in graph.edges if edge.role == "axiom"]

        assert len(ontology_edges) == 18


def test_refresh_derived_edges_materializes_relations_from_migrated_structure() -> None:
    migrations = Path(__file__).resolve().parents[2] / "examples" / "migrations"
    with MigrationRunner() as runner:
        runner.apply_all(migrations)
        runner.refresh_derived_edges()

        rows = runner._require_projection().execute(
            "MATCH ()-[d:D {relation: 'subclass_of'}]->() RETURN count(*) AS c"
        )

    assert rows[0]["c"] > 0


def test_migration_runner_applies_one_file_atomically(tmp_path: Path) -> None:
    migration = tmp_path / "V0001__broken.cypher"
    migration.write_text(
        "\n".join(
            [
                "// Broken migration.",
                "MERGE (n:N {uid: '0x01', kind: 'Ontology'});",
                "THIS IS NOT VALID;",
            ]
        )
    )

    with MigrationRunner() as runner:
        with pytest.raises(RuntimeError, match="Parser exception"):
            runner.apply_file(migration)

        assert runner.node_count == 0
        assert runner.edge_count == 0
        assert runner.applied_migrations == []


def test_migration_runner_recovers_applied_ids_from_projection(
    tmp_path: Path,
) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "V0001__ontology.cypher").write_text(
        "MERGE (n:N {uid: '0x01', kind: 'Ontology'});"
    )
    database_path = tmp_path / "projection.lbug"
    with MigrationRunner(start_from=database_path):
        pass

    with MigrationRunner(start_from=database_path) as runner:
        result = runner.apply_all(migrations)

        assert [record.migration_id for record in result.applied] == ["V0001"]
        assert runner.applied_migrations == ["V0001"]
        assert runner.node_count == 1

    with MigrationRunner(start_from=database_path) as runner:
        result = runner.apply_all(migrations)

        assert result.applied == []
        assert runner.applied_migrations == ["V0001"]
        assert runner.node_count == 1


def test_migration_runner_rejects_duplicate_ids_before_executing(
    tmp_path: Path,
) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "V0001__first.cypher").write_text("MERGE (n:N {uid: '0x01', kind: 'Ontology'});")
    (migrations / "V0001__second.cypher").write_text("MERGE (n:N {uid: '0x02', kind: 'Ontology'});")

    with MigrationRunner() as runner:
        with pytest.raises(MigrationError, match="Duplicate migration id 'V0001'"):
            runner.apply_all(migrations)

        assert runner.node_count == 0
        assert runner.edge_count == 0
        assert runner.applied_migrations == []


def test_migration_uid_helpers_are_stable_and_namespaced() -> None:
    class_uid = scalar_uid("Class", "https://example.org/Person")
    repeated_class_uid = scalar_uid("Class", "https://example.org/Person")
    axiom_with_same_text = axiom_uid(
        "Class",
        [("iri", "https://example.org/Person")],
    )

    assert class_uid == repeated_class_uid
    assert class_uid == "0x7bacc7c895c2521b070dbf8b70274c77"
    assert class_uid.startswith("0x")
    assert len(class_uid) == len("0x") + MIGRATION_UID_DIGEST_HEX_LENGTH
    assert axiom_with_same_text == "0x9339d9cb6a672cd0fc1ff30fc2bb3ae3"
    assert class_uid != axiom_with_same_text


def test_migration_template_environment_uses_public_uid_helpers(tmp_path: Path) -> None:
    migration = tmp_path / "V0001__uids.cypher"
    expected_scalar_uid = scalar_uid("Class", "https://example.org/Person")
    expected_axiom_uid = axiom_uid("SubClassOf", [("sub", expected_scalar_uid)])
    migration.write_text(
        "\n".join(
            [
                "{%- set person_uid = scalar_uid('Class', 'https://example.org/Person') -%}",
                "{%- set ax_uid = axiom_uid('SubClassOf', [",
                "    ('sub', person_uid)",
                "]) -%}",
                "MERGE (person:N {uid: '<< person_uid >>', kind: 'Class', "
                "iri: 'https://example.org/Person'})",
                "MERGE (axiom:N {uid: '<< ax_uid >>', kind: 'SubClassOf'})",
                "MERGE (axiom)-[:E {role: 'sub', position: 0}]->(person);",
            ]
        )
    )

    with MigrationRunner() as runner:
        runner.apply_file(migration)
        graph = runner.graph()

    assert {node.uid for node in graph.nodes} >= {expected_scalar_uid, expected_axiom_uid}


def test_migration_runner_raises_projection_storage_error_after_close() -> None:
    runner = MigrationRunner()
    runner.close()

    with pytest.raises(ProjectionStorageError, match="MigrationRunner has been closed"):
        _ = runner.node_count

    with pytest.raises(ProjectionStorageError, match="MigrationRunner has been closed"):
        _ = runner.edge_count

    with pytest.raises(ProjectionStorageError, match="MigrationRunner has been closed"):
        runner.graph()

    with pytest.raises(ProjectionStorageError, match="MigrationRunner has been closed"):
        runner.build_database()


def test_migration_runner_build_database_returns_readonly_projection(tmp_path: Path) -> None:
    migration = tmp_path / "V0001__ontology.cypher"
    migration.write_text("MERGE (n:N {uid: '0x01', kind: 'Ontology'});")

    runner = MigrationRunner()
    runner.apply_file(migration)

    projection = runner.build_database()
    try:
        assert projection.node_count == 1
        assert projection.edge_count == 0
    finally:
        projection.close()

    with pytest.raises(ProjectionStorageError, match="MigrationRunner has been closed"):
        runner.graph()


def test_migration_runner_apply_file_raises_projection_storage_error_after_close(
    tmp_path: Path,
) -> None:
    runner = MigrationRunner()
    runner.close()

    with pytest.raises(ProjectionStorageError, match="MigrationRunner has been closed"):
        runner.apply_file(tmp_path / "V0001__noop.cypher")
