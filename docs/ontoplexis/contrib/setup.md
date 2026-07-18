---
title: Development Setup
---

# Development Setup

Ontoplexis is developed within [Wise Ideas](https://github.com/wise-ideas);
this guide covers the toolchain and workflow its developers use. Bug reports
are welcome on the
[issue tracker](https://github.com/wise-ideas/ontotheke/issues).

## Toolchain

- Python 3.11+ with [uv](https://docs.astral.sh/uv/)
- A Java 17+ runtime (runs [ROBOT](http://robot.obolibrary.org/), the OWLAPI
  test oracle; dev-only, downloaded by `make fetch-robot`, never shipped)

!!! warning "Avoid snap-hosted toolchains"
    Install `uv` and Java outside any snap-packaged editor:
    snap-private tool installs disappear when the snap updates, silently
    breaking `.venv` interpreter symlinks.

## Workflow

```bash
make sync                 # install the full workspace
make check-ontoplexis     # download the ROBOT jar if needed, then ruff + ruff format --check + ty + pytest
make test-ontoplexis      # download the ROBOT jar if needed, then pytest only
make docs                 # build the combined documentation site into site/
make serve-docs     # live-preview on 127.0.0.1:8001
```

Round-trip tests skip when the oracle jar is missing, so a full validation
must download it first — `make check-ontoplexis` and `make test-ontoplexis` both do.

## Invariants to preserve

- **No per-construct vocabulary code, in any language.** The walker in
  `owlxml.py` is generic; kind-specific knowledge lives only in the `_ROLES`
  data table.
- **Round-trip fidelity is proven by the reference implementation** — the
  functional-syntax comparison tests in `tests/test_roundtrip.py`, which run
  OWLAPI as a dev-only oracle (`tests/oracle.py`). If you change the walker,
  those tests are the gate.
- **The public surface is pinned** by `tests/test_public_contract.py`.
