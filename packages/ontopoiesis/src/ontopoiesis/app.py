import logging
from os import getenv
from typing import Optional

import dotenv
import typer
import typer.core

from ontopoiesis.commands.build import build
from ontopoiesis.commands.convert import convert
from ontopoiesis.commands.diff import diff
from ontopoiesis.commands.export import export
from ontopoiesis.commands.impact import impact
from ontopoiesis.commands.lint_command import lint
from ontopoiesis.commands.migrate import migrate
from ontopoiesis.commands.query import query
from ontopoiesis.commands.reason import reason
from ontopoiesis.commands.render_command import render
from ontopoiesis.commands.resolve import resolve
from ontopoiesis.commands.test import test
from ontopoiesis.errors import translate_cli_errors


class _ErrorHandlingGroup(typer.core.TyperGroup):
    def invoke(self, ctx: typer.core._click.Context) -> object:
        with translate_cli_errors():
            return super().invoke(ctx)


app = typer.Typer(
    cls=_ErrorHandlingGroup,
    no_args_is_help=True,
    help="ontopoiesis operator CLI.",
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
)


@app.callback()
def main(
    log_level: Optional[str] = typer.Option(
        None,
        "--log-level",
        help="Log level: DEBUG, INFO, WARNING, ERROR (default: INFO, or LOG_LEVEL env var).",
        metavar="LEVEL",
    ),
) -> None:
    """Run the ontopoiesis operator CLI."""
    dotenv.load_dotenv()
    level_name = (log_level or getenv("LOG_LEVEL", "INFO")).upper()
    if level_name not in logging.getLevelNamesMapping():
        raise typer.BadParameter(
            f"Unknown log level {level_name!r}. Use DEBUG, INFO, WARNING, or ERROR.",
            param_hint="'--log-level'",
        )
    logging.basicConfig(
        level=level_name,
        format="%(levelname)s %(name)s: %(message)s",
    )


app.command()(build)
app.command()(convert)
app.command()(resolve)
app.command()(reason)
app.command()(diff)
app.command()(export)
app.add_typer(impact, name="impact")
app.command()(migrate)
app.command()(query)
app.command()(render)
app.command()(lint)
app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})(test)
