from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

import pytest
from _pytest._code.code import TerminalRepr, TracebackStyle
from _pytest.outcomes import Exit
from ontoplexis import Projection

from ontopoiesis.cli_ui import DEFAULT_MAX_ROWS, format_violation_rows
from ontopoiesis.cypher_test.discovery import DEFAULT_CYPHER_FILE_PATTERNS, is_warning_cypher_path

_log = logging.getLogger(__name__)

QueryRow = dict[str, object]

RUNTIME_KEY: pytest.StashKey[Projection] = pytest.StashKey()
WARNING_KEY: pytest.StashKey[list["CypherWarning"]] = pytest.StashKey()


class CypherFailure(Exception):
    def __init__(self, rows: list[QueryRow]) -> None:
        self.rows = rows

    def render(self, max_rows: int | None = DEFAULT_MAX_ROWS) -> str:
        return format_violation_rows(self.rows, max_rows=max_rows)


@dataclass(frozen=True)
class CypherWarning:
    path: Path
    rows: list[QueryRow]


class CypherFile(pytest.File):
    def collect(self):
        if is_warning_cypher_path(self.path):
            item = CypherWarningItem.from_parent(self, name=self.path.name)
            item.add_marker("cypher_warning")
        else:
            item = CypherItem.from_parent(self, name=self.path.name)
            item.add_marker("cypher")
        yield item


class CypherItem(pytest.Item):
    def runtest(self) -> None:
        runtime = self.config.stash[RUNTIME_KEY]
        query = self.path.read_text()
        result = runtime.execute(query)
        if result:
            raise CypherFailure(result)

    def repr_failure(
        self,
        excinfo: pytest.ExceptionInfo[BaseException],
        style: TracebackStyle | None = None,
    ) -> str | TerminalRepr:
        if isinstance(excinfo.value, CypherFailure):
            verbose = self.config.option.verbose
            max_rows = _max_rows_for_verbosity(verbose)
            return excinfo.value.render(max_rows=max_rows)
        return super().repr_failure(excinfo, style=style)

    def reportinfo(self) -> tuple[Path, int, str]:
        return self.path, 0, f"cypher test: {self.name}"


class CypherWarningItem(pytest.Item):
    def runtest(self) -> None:
        runtime = self.config.stash[RUNTIME_KEY]
        query = self.path.read_text()
        result = runtime.execute(query)
        if result:
            warnings = self.config.stash[WARNING_KEY]
            warnings.append(CypherWarning(path=self.path, rows=result))

    def reportinfo(self) -> tuple[Path, int, str]:
        return self.path, 0, f"cypher warning: {self.name}"


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("ontopoiesis")
    group.addoption("--ontology", action="store", help=".lbug graph to test")
    parser.addini(
        "cypher_files",
        type="args",
        default=list(DEFAULT_CYPHER_FILE_PATTERNS),
        help="Cypher test file discovery patterns",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "cypher: projection graph data-quality check")
    config.addinivalue_line(
        "markers", "cypher_warning: advisory projection graph data-quality check"
    )


def pytest_collect_file(file_path: Path, parent: pytest.Collector) -> CypherFile | None:
    if file_path.suffix != ".cypher":
        return None
    patterns = parent.config.getini("cypher_files")
    if not _is_explicit_target(file_path, parent.config.args) and not any(
        file_path.match(pattern) for pattern in patterns
    ):
        return None
    return CypherFile.from_parent(parent, path=file_path)


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    del items
    session.config.stash[WARNING_KEY] = []
    ontology_path = session.config.getoption("ontology")
    if not ontology_path:
        raise Exit("--ontology is required for cypher tests", returncode=2)
    try:
        runtime = _build_runtime(Path(ontology_path))
    except ValueError as exc:
        raise Exit(str(exc), returncode=2) from exc
    session.config.stash[RUNTIME_KEY] = runtime
    runtime.__enter__()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    del exitstatus
    runtime = session.config.stash.get(RUNTIME_KEY, None)
    if runtime is not None:
        runtime.__exit__(None, None, None)


def open_cypher_runtime(input_path: Path) -> Projection:
    """Open a query runtime for one persisted projection."""
    if input_path.suffix.lower() != ".lbug":
        raise ValueError(f"Cypher tests require a .lbug projection, got {input_path}.")
    return Projection.open(input_path)


def _build_runtime(input_path: Path) -> Projection:
    _log.debug("Opening Cypher runtime for %s", input_path)
    t0 = time.monotonic()
    runtime = open_cypher_runtime(input_path)
    elapsed = time.monotonic() - t0
    _log.info("Cypher runtime ready in %.1fs", elapsed)
    return runtime


def _max_rows_for_verbosity(verbose: int) -> int | None:
    if verbose >= 2:
        return None
    if verbose >= 1:
        return DEFAULT_MAX_ROWS
    return 0


def _is_explicit_target(path: Path, config_args: list[str]) -> bool:
    resolved_path = path.resolve()
    for arg in config_args:
        candidate = Path(arg)
        if candidate.exists() and candidate.resolve() == resolved_path:
            return True
    return False


def pytest_terminal_summary(terminalreporter: pytest.TerminalReporter) -> None:
    warnings = terminalreporter.config.stash.get(WARNING_KEY, [])
    if not warnings:
        return

    terminalreporter.section("cypher warnings", sep="=")
    verbose = terminalreporter.config.option.verbose
    max_rows = _max_rows_for_verbosity(verbose)
    for warning in warnings:
        terminalreporter.line(f"WARN {warning.path.name}")
        terminalreporter.line(format_violation_rows(warning.rows, max_rows=max_rows))
