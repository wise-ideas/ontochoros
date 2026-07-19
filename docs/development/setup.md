---
title: Development Setup
---

# Development Setup

The Ontochoros packages are developed within
[Wise Ideas](https://github.com/wise-ideas) as a single
[uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/); this
guide covers the toolchain and workflow shared by all of them. Bug reports are
welcome on the
[issue tracker](https://github.com/wise-ideas/ontochoros/issues).

## Toolchain

- Python 3.11+ with [uv](https://docs.astral.sh/uv/)
- A Java 17+ runtime (runs [ROBOT](http://robot.obolibrary.org/), the OWLAPI
  test oracle for Ontoplexis; dev-only, downloaded by `make fetch-robot`,
  never shipped)

!!! warning "Avoid snap-hosted toolchains"
    Install `uv` and Java outside any snap-packaged editor:
    snap-private tool installs disappear when the snap updates, silently
    breaking `.venv` interpreter symlinks.

## Workflow

```bash
make sync                  # install the full workspace
make check                 # lockfile check, then ruff + ruff format --check + ty + pytest for every package
make check-<package>       # the same checks for one package, e.g. make check-ontoplexis
make test-<package>        # pytest only, e.g. make test-ontopoiesis
make docs                  # build this documentation site into site/
uv run zensical serve      # live-preview the site on localhost:8000
```

The Ontoplexis checks depend on the ROBOT oracle jar: round-trip tests skip
when it is missing, so a full validation must download it first —
`make check-ontoplexis` and `make test-ontoplexis` both do.

## Releases

Each package releases independently via the manual release workflow; see the
[README](https://github.com/wise-ideas/ontochoros#releases) for the process.

## Package internals

Package-specific invariants and architecture notes live with each package:

- [Ontoplexis internals](../ontoplexis/contrib/internals.md)
- [Ontopoiesis internals](../ontopoiesis/contrib/index.md)
