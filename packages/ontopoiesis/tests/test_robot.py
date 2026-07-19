"""Failure modes of the ROBOT shim's subprocess boundary.

The happy path runs for real in test_commands.py behind the jar-gated marker;
these tests pin how each way the subprocess can fail is surfaced, with the
subprocess call itself mocked — the one true process boundary here.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ontopoiesis.robot import (
    ROBOT_JAR_ENV,
    RobotCommandError,
    RobotUnavailableError,
    convert_to_owlxml,
)


@pytest.fixture
def fake_jar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    jar = tmp_path / "robot.jar"
    jar.write_bytes(b"not a real jar")
    monkeypatch.setenv(ROBOT_JAR_ENV, str(jar))
    return jar


def _convert(tmp_path: Path) -> None:
    convert_to_owlxml(tmp_path / "in.ttl", tmp_path / "out.owx")


def test_missing_java_binary_reports_unavailable_with_install_hint(
    fake_jar: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def raise_missing(*args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory", "java")

    monkeypatch.setattr("ontopoiesis.robot.subprocess.run", raise_missing)

    with pytest.raises(RobotUnavailableError, match="'java'") as excinfo:
        _convert(tmp_path)
    assert "Java 17+" in str(excinfo.value)


def test_timeout_reports_unavailable_with_the_command_name(
    fake_jar: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def raise_timeout(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs["timeout"])

    monkeypatch.setattr("ontopoiesis.robot.subprocess.run", raise_timeout)

    with pytest.raises(RobotUnavailableError, match="convert timed out"):
        _convert(tmp_path)


def test_os_error_reports_unavailable(
    fake_jar: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def raise_os_error(*args, **kwargs):
        raise OSError("exec format error")

    monkeypatch.setattr("ontopoiesis.robot.subprocess.run", raise_os_error)

    with pytest.raises(RobotUnavailableError, match="exec format error"):
        _convert(tmp_path)


def test_nonzero_exit_surfaces_robots_own_message(
    fake_jar: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(cmd, **kwargs):
        return subprocess.CompletedProcess(
            cmd, returncode=1, stdout="", stderr="UNPARSEABLE ONTOLOGY\n"
        )

    monkeypatch.setattr("ontopoiesis.robot.subprocess.run", fail)

    with pytest.raises(RobotCommandError, match="UNPARSEABLE ONTOLOGY"):
        _convert(tmp_path)


def test_nonzero_exit_without_output_falls_back_to_a_generic_message(
    fake_jar: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_silently(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="")

    monkeypatch.setattr("ontopoiesis.robot.subprocess.run", fail_silently)

    with pytest.raises(RobotCommandError, match="ROBOT convert failed."):
        _convert(tmp_path)
