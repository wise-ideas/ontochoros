"""Shared test fixtures."""

from __future__ import annotations

import hashlib
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest
from ontoplexis import Ontology

WriteLbug = Callable[[Path, str], Path]


@pytest.fixture(scope="session")
def write_lbug(tmp_path_factory: pytest.TempPathFactory) -> WriteLbug:
    """Copy-on-write projection builder: one real build per distinct document.

    Building a projection costs seconds of engine-side schema and derive
    work; copying the saved single-file database costs under a millisecond.
    Isolation is preserved — every call hands back a fresh mutable copy.
    """
    template_dir = tmp_path_factory.mktemp("lbug-templates")
    templates: dict[str, Path] = {}

    def write(path: Path, document: str) -> Path:
        key = hashlib.sha256(document.encode("utf-8")).hexdigest()[:16]
        template = templates.get(key)
        if template is None:
            template = template_dir / f"{key}.lbug"
            Ontology.from_owlxml(document).save_projection(template).close()
            templates[key] = template
        shutil.copy(template, path)
        return path

    return write
