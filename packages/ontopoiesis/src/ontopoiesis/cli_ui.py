from __future__ import annotations

from collections.abc import Iterable, Sequence
from contextlib import nullcontext

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

_THEME = Theme(
    {
        "accent": "bold bright_cyan",
        "muted": "dim white",
        "success": "bold green",
        "warning": "bold yellow",
        "key": "bold bright_cyan",
    }
)

console = Console(theme=_THEME, soft_wrap=True)
err_console = Console(stderr=True, theme=_THEME, soft_wrap=True)

DEFAULT_MAX_ROWS = 5

QueryRow = dict[str, object]


def print_stage(index: int, total: int, label: str) -> None:
    console.print(f"[accent]Stage {index}/{total}[/accent] [muted]{label}[/muted]")


def stage_spinner(label: str):
    if not console.is_terminal:
        return nullcontext()
    return console.status(f"[accent]{label}[/accent]", spinner="dots")


def print_notice(message: str, *, err: bool = False) -> None:
    target = err_console if err else console
    style = "warning" if err else "muted"
    target.print(Text(message, style=style))


def print_path_action(action: str, path: object) -> None:
    console.print(Text.assemble((f"{action} ", "success"), (str(path), "accent")))


def print_summary(title: str, rows: Sequence[tuple[str, object]]) -> None:
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="key", justify="right")
    grid.add_column(overflow="fold")
    for key, value in rows:
        rendered = f"{value:,}" if isinstance(value, int) else str(value)
        grid.add_row(str(key), rendered)
    console.print(Panel.fit(grid, title=title, border_style="accent", padding=(0, 1)))


def print_query_table(rows: Iterable[dict[str, object]]) -> None:
    materialized = list(rows)
    if not materialized:
        return
    table = Table(box=box.SIMPLE_HEAVY, header_style="accent", border_style="accent")
    for header in materialized[0]:
        table.add_column(str(header))
    for row in materialized:
        table.add_row(*(str(row.get(header, "")) for header in materialized[0]))
    console.print(table)


def print_violation_rows(
    rows: Sequence[QueryRow],
    max_rows: int | None = DEFAULT_MAX_ROWS,
    *,
    err: bool = False,
) -> None:
    """Print violation rows as a Rich table."""
    target = err_console if err else console
    _render_violation_rows_to(target, rows, max_rows, verbosity_hint=False)


def format_violation_rows(
    rows: Sequence[QueryRow],
    max_rows: int | None = DEFAULT_MAX_ROWS,
) -> str:
    """Render violation rows to a string, for use in pytest output."""
    capture = Console(record=True, highlight=False, theme=_THEME)
    _render_violation_rows_to(capture, rows, max_rows, verbosity_hint=True)
    return capture.export_text()


def _render_violation_rows_to(
    target: Console,
    rows: Sequence[QueryRow],
    max_rows: int | None,
    *,
    verbosity_hint: bool,
) -> None:
    target.print(f"query returned {len(rows)} violation row(s)")
    if rows and (max_rows is None or max_rows > 0):
        displayed = rows if max_rows is None else rows[:max_rows]
        table = Table(box=box.SIMPLE_HEAVY, header_style="accent", border_style="accent")
        for header in displayed[0]:
            table.add_column(str(header))
        for row in displayed:
            table.add_row(*(str(row.get(h, "")) for h in displayed[0]))
        target.print(table)
    if max_rows is not None and len(rows) > max_rows:
        hidden = len(rows) - max_rows
        if verbosity_hint:
            hint = (
                "run with -v to see a sample"
                if max_rows == 0
                else f"{hidden} more, run with -vv to show all"
            )
        else:
            hint = f"{hidden} more row(s) not shown"
        target.print(f"  … {hint}")
