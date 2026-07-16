"""Optional ROBOT shim: format conversion and reasoner materialization.

ROBOT (the OBO community's OWLAPI CLI) stays an **external, opt-in** tool: it
is never bundled, never a hard dependency, and never touches ontoplexis. The
shim shells out to a user-provided jar, discovered through the ``ROBOT_JAR``
environment variable (dotenv-loaded, so a project ``.env`` works), and adds a
JVM requirement only on the commands that use it (``convert``, ``reason``).

Reasoning stays outside the graph: ``reason`` materializes inferred axioms
into a *new OWL/XML document* via the chosen reasoner. Once built, inferred
axioms are ordinary told structure — the derived-edge cache picks them up like
any other axiom — with each one annotated ``is_inferred true`` by default so
the provenance stays queryable.

ROBOT's errors are surfaced verbatim: conversion can be lossy for RDF that is
not valid OWL 2, and the reasoner's complaints are the actionable part.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from ontopoiesis.errors import OntopoiesisDomainError

ROBOT_JAR_ENV = "ROBOT_JAR"

_TIMEOUT_SECONDS = 600.0

_INSTALL_HINT = (
    f"Set the {ROBOT_JAR_ENV} environment variable (or a .env entry) to the path of a "
    "ROBOT jar, downloadable from https://github.com/ontodev/robot/releases. "
    "A Java 17+ runtime must be on PATH."
)


class RobotUnavailableError(OntopoiesisDomainError):
    """ROBOT (or the JVM) could not be located or executed."""


class RobotCommandError(OntopoiesisDomainError):
    """ROBOT ran and rejected the request; carries ROBOT's own message."""


def discover_jar() -> Path:
    """Locate the ROBOT jar from the environment, or fail with the recipe."""
    configured = os.environ.get(ROBOT_JAR_ENV)
    if not configured:
        raise RobotUnavailableError(f"No ROBOT jar configured. {_INSTALL_HINT}")
    jar = Path(configured)
    if not jar.is_file():
        raise RobotUnavailableError(f"{ROBOT_JAR_ENV}={configured} does not exist. {_INSTALL_HINT}")
    return jar


def convert_to_owlxml(input_path: Path, output_path: Path) -> None:
    """Convert any ROBOT-readable ontology document to OWL/XML.

    The input format is inferred from the file extension, as ROBOT does
    (``.ttl``, ``.owl``, ``.ofn``, ``.omn``, ``.obo``, ``.json``, …).
    """
    _run("convert", "--input", str(input_path), "--format", "owx", "--output", str(output_path))


def reason_to_owlxml(
    input_path: Path,
    output_path: Path,
    *,
    reasoner: str = "ELK",
    annotate: bool = True,
    include_indirect: bool = False,
) -> None:
    """Materialize inferred axioms into a new OWL/XML document.

    Runs ``robot reason``: the output contains the original axioms plus the
    reasoner's inferences (direct, non-redundant subclass axioms by default;
    ``include_indirect`` asserts the full inferred hierarchy so every entailed
    subsumption is a single edge). With ``annotate``, each inferred axiom
    carries an ``is_inferred true`` annotation, so told and inferred structure
    stay distinguishable in the built projection.
    """
    _run(
        "reason",
        "--reasoner",
        reasoner,
        "--annotate-inferred-axioms",
        "true" if annotate else "false",
        "--include-indirect",
        "true" if include_indirect else "false",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
    )


def _run(*args: str) -> None:
    jar = discover_jar()
    command = ["java", "-jar", str(jar), *args]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RobotUnavailableError(f"Failed to execute {exc.filename!r}. {_INSTALL_HINT}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RobotUnavailableError(
            f"ROBOT {args[0]} timed out after {_TIMEOUT_SECONDS:.0f}s."
        ) from exc
    except OSError as exc:
        raise RobotUnavailableError(f"Failed to execute ROBOT: {exc}") from exc
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"ROBOT {args[0]} failed."
        raise RobotCommandError(message)


__all__ = [
    "ROBOT_JAR_ENV",
    "RobotCommandError",
    "RobotUnavailableError",
    "convert_to_owlxml",
    "discover_jar",
    "reason_to_owlxml",
]
