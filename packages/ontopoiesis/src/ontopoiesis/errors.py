from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import typer
from ontoplexis import OwlXmlStructureError, ProjectionStorageError


class OntopoiesisDomainError(Exception):
    """Base for ontopoiesis errors that should render as user-facing CLI messages."""


class RenderDependencyError(OntopoiesisDomainError, RuntimeError):
    """Raised when a required external render dependency (e.g. Graphviz) is unavailable."""


_CLI_DOMAIN_ERROR_TYPES = (
    OntopoiesisDomainError,
    OwlXmlStructureError,
    ProjectionStorageError,
)


def _exception_message(exc: BaseException) -> str:
    if len(exc.args) == 1 and isinstance(exc.args[0], str):
        return exc.args[0]
    return str(exc)


def _collect_cli_error_messages(exc: BaseException) -> list[str] | None:
    if isinstance(exc, _CLI_DOMAIN_ERROR_TYPES):
        return [_exception_message(exc)]
    if isinstance(exc, BaseExceptionGroup):
        messages: list[str] = []
        for nested in exc.exceptions:
            nested_messages = _collect_cli_error_messages(nested)
            if nested_messages is None:
                return None
            messages.extend(nested_messages)
        return list(dict.fromkeys(messages))
    return None


def _format_cli_error_message(messages: list[str]) -> str:
    if len(messages) == 1:
        return messages[0]
    bullet_list = "\n".join(f"- {message}" for message in messages)
    return f"Multiple errors:\n{bullet_list}"


def raise_cli_error(exc: Exception) -> None:
    messages = _collect_cli_error_messages(exc)
    if messages is not None:
        raise typer.BadParameter(_format_cli_error_message(messages)) from exc
    raise exc


@contextmanager
def translate_cli_errors() -> Iterator[None]:
    try:
        yield
    except Exception as exc:
        raise_cli_error(exc)
