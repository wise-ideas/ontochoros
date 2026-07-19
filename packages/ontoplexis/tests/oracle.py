"""ROBOT (OWLAPI) as a dev-only test oracle.

Nothing here ships with the package. ROBOT — the OBO community's OWLAPI CLI —
is downloaded on demand ('make fetch-robot', pinned in the Makefile) so the
round-trip fidelity tests can compare the walker's output against the
reference implementation. Requires a Java 17+ runtime on PATH.

Conversions are memoized on disk under ``.cache/oracle/<jar-digest>/``, keyed
by the full request content (formats plus source document). The corpus is
static and the walker deterministic, so a warm cache skips almost every JVM
launch; any change to an input, or to the jar itself, re-converts by
construction. ROBOT failures are never cached.
"""

from __future__ import annotations

import hashlib
import logging
import subprocess
import tempfile
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_log = logging.getLogger(__name__)

JAR = Path(__file__).resolve().parents[1] / ".cache" / "robot" / "robot.jar"

_ORACLE_CACHE = Path(__file__).resolve().parents[1] / ".cache" / "oracle"

# File extensions ROBOT uses to infer document formats.
_EXTENSIONS = {
    "owlxml": "owx",
    "functional": "ofn",
    "turtle": "ttl",
    "rdfxml": "owl",
    "manchester": "omn",
}


@dataclass(frozen=True, slots=True)
class OracleConfig:
    """Configuration for the ROBOT oracle subprocess."""

    jar: Path
    java_bin: str = "java"
    timeout: float = 300.0


class OracleUnavailableError(RuntimeError):
    """Raised when the ROBOT jar cannot be executed."""


class OracleRequestError(RuntimeError):
    """Raised when ROBOT rejects a validly delivered request."""


def convert_document(
    config: OracleConfig,
    source: str,
    *,
    target_format: str,
    source_format: str,
) -> str:
    """Convert an ontology document to another OWL 2 serialization."""
    if not config.jar.exists():
        raise OracleUnavailableError(
            f"ROBOT jar not found at {config.jar}. Download it with 'make fetch-robot'."
        )
    cache_path = _conversion_cache_path(
        config.jar, source, source_format=source_format, target_format=target_format
    )
    if cache_path.exists():
        return cache_path.read_text()
    with tempfile.TemporaryDirectory(prefix="ontoplexis-oracle-") as tmp:
        source_path = Path(tmp) / f"source.{_EXTENSIONS[source_format]}"
        target_path = Path(tmp) / f"target.{_EXTENSIONS[target_format]}"
        source_path.write_text(source)
        _run_robot(
            config,
            "convert",
            "--input",
            str(source_path),
            "--format",
            _EXTENSIONS[target_format],
            "--output",
            str(target_path),
        )
        result = target_path.read_text()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        staged = cache_path.with_suffix(".tmp")
        staged.write_text(result)
        staged.replace(cache_path)
        return result


@lru_cache(maxsize=4)
def _jar_digest(jar: Path) -> str:
    return hashlib.sha256(jar.read_bytes()).hexdigest()[:16]


def _conversion_cache_path(
    jar: Path, source: str, *, source_format: str, target_format: str
) -> Path:
    request = f"{source_format}\x00{target_format}\x00{source}"
    key = hashlib.sha256(request.encode("utf-8")).hexdigest()
    return _ORACLE_CACHE / _jar_digest(jar) / f"{key}.{_EXTENSIONS[target_format]}"


def _run_robot(config: OracleConfig, *args: str) -> None:
    cmd = [config.java_bin, "-jar", str(config.jar), *args]
    _log.debug("ROBOT %s: starting (timeout=%.0fs)", args[0], config.timeout)
    started = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise OracleUnavailableError(f"ROBOT {args[0]} timed out after {config.timeout:.0f}s.")
    except FileNotFoundError as exc:
        raise OracleUnavailableError(
            f"Failed to execute ROBOT because {exc.filename!r} was not found."
        ) from exc
    except OSError as exc:
        raise OracleUnavailableError(f"Failed to execute ROBOT: {exc}") from exc

    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or f"ROBOT {args[0]} failed."
        raise OracleRequestError(error)
    _log.debug("ROBOT %s: completed in %.1fs", args[0], time.monotonic() - started)
