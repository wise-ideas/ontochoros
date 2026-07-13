import logging
from enum import Enum
from pathlib import Path

import typer
from ontoplexis import NODE_TABLE, RELATIONSHIP_TABLE, Projection

from ontopoiesis.cli_ui import print_notice, print_query_table
from ontopoiesis.path_validation import require_lbug_input

_log = logging.getLogger(__name__)

impact = typer.Typer(
    no_args_is_help=True,
    help="Trace structural references to or from one named entity in a Ladybug projection.",
)

_MAX_TRAVERSAL_DEPTH = 30


class _ImpactDirection(str, Enum):
    UPSTREAM = "upstream"
    DOWNSTREAM = "downstream"


class _ImpactSeedKind(str, Enum):
    IRI = "iri"
    UID = "uid"


def _impact_query(*, seed_kind: _ImpactSeedKind, direction: _ImpactDirection) -> str:
    seed_filter = f"seed.{seed_kind.value} = $seed"
    pattern = (
        f"(n:{NODE_TABLE})-[:{RELATIONSHIP_TABLE}* SHORTEST 1..{_MAX_TRAVERSAL_DEPTH}]->(seed)"
        if direction == _ImpactDirection.UPSTREAM
        else f"(seed)-[:{RELATIONSHIP_TABLE}* SHORTEST 1..{_MAX_TRAVERSAL_DEPTH}]->(n:{NODE_TABLE})"
    )
    return (
        f"MATCH (seed:{NODE_TABLE}) WHERE {seed_filter} "
        f"MATCH p = {pattern} "
        "RETURN DISTINCT n.uid AS uid, n.kind AS kind, length(p) AS depth, n.iri AS iri "
        "ORDER BY depth, kind, uid"
    )


def _query_impact(
    projection_path: Path,
    seed: str,
    *,
    seed_kind: _ImpactSeedKind,
    direction: _ImpactDirection,
) -> list[dict[str, object]]:
    _log.info(
        "Querying %s impact for %s=%s in %s", direction, seed_kind.value, seed, projection_path
    )
    with Projection.open(projection_path) as projection:
        rows = projection.execute(
            _impact_query(seed_kind=seed_kind, direction=direction),
            parameters={"seed": seed},
        )
    _log.info("Impact query returned %d rows", len(rows))
    return rows


def _run_impact(
    input_path: Path,
    *,
    iri: str | None,
    uid: str | None,
    direction: _ImpactDirection,
) -> None:
    require_lbug_input(input_path)
    seed_kind, seed = _resolve_seed(iri=iri, uid=uid)
    rows = _query_impact(input_path, seed, seed_kind=seed_kind, direction=direction)
    if not rows:
        print_notice(f"No constructs found for {seed_kind.value} {seed}.")
        return
    print_query_table(rows)


def _resolve_seed(*, iri: str | None, uid: str | None) -> tuple[_ImpactSeedKind, str]:
    if bool(iri) == bool(uid):
        raise typer.BadParameter("Pass exactly one of --iri or --uid.")
    if iri:
        return _ImpactSeedKind.IRI, iri
    if uid:
        return _ImpactSeedKind.UID, uid
    raise typer.BadParameter("Pass exactly one of --iri or --uid.")


@impact.command()
def upstream(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    iri: str | None = typer.Option(None, "--iri"),
    uid: str | None = typer.Option(None, "--uid"),
) -> None:
    """Show constructs that reference the named entity."""
    _run_impact(input_path, iri=iri, uid=uid, direction=_ImpactDirection.UPSTREAM)


@impact.command()
def downstream(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    iri: str | None = typer.Option(None, "--iri"),
    uid: str | None = typer.Option(None, "--uid"),
) -> None:
    """Show constructs reachable from the named entity."""
    _run_impact(input_path, iri=iri, uid=uid, direction=_ImpactDirection.DOWNSTREAM)
