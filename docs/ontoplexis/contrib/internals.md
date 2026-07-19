---
title: Internals
---

# Internals

This page covers invariants specific to working on Ontoplexis. For the shared
toolchain and workflow, see the
[development setup guide](../../development/setup.md).

## Invariants to preserve

- **No per-construct vocabulary code, in any language.** The walker in
  `owlxml.py` is generic; kind-specific knowledge lives only in the `_ROLES`
  data table.
- **Round-trip fidelity is proven by the reference implementation** — the
  functional-syntax comparison tests in `tests/test_roundtrip.py`, which run
  OWLAPI as a dev-only oracle (`tests/oracle.py`). If you change the walker,
  those tests are the gate.
- **The public surface is pinned** by `tests/test_public_contract.py`.
