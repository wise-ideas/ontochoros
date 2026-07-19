from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path

import pytest

import ontophora.constructs as concrete_package
from ontophora._registry import (
    construct_json_schema,
    construct_metadata,
    construct_metadata_by_kind,
    construct_types,
)
from ontophora.constructs.base import BaseConstruct


def _concrete_construct_types() -> set[type[BaseConstruct]]:
    construct_types: set[type[BaseConstruct]] = set()
    for module_info in pkgutil.iter_modules(concrete_package.__path__):
        if module_info.name in {"base", "iri", "types"}:
            continue
        module = importlib.import_module(f"{concrete_package.__name__}.{module_info.name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module.__name__:
                continue
            if issubclass(obj, BaseConstruct):
                construct_types.add(obj)
    return construct_types


def test_construct_catalog_covers_every_concrete_construct_type() -> None:
    assert set(construct_types) == _concrete_construct_types()


def test_construct_catalog_is_the_only_registration_manifest() -> None:
    model_dir = Path(__file__).resolve().parents[2] / "src" / "ontophora" / "model"

    assert not (model_dir / "models").exists()


def test_construct_metadata_have_unique_kinds() -> None:
    assert len({metadata.kind for metadata in construct_metadata}) == len(construct_metadata)


def test_construct_metadata_by_kind_matches_metadata() -> None:
    assert construct_metadata_by_kind() == {
        metadata.kind: metadata for metadata in construct_metadata
    }


def test_construct_json_schema_uses_discriminator() -> None:
    schema = construct_json_schema()

    assert schema["discriminator"]["propertyName"] == "kind"
    assert set(schema["discriminator"]["mapping"]) == set(construct_metadata_by_kind())
    assert "oneOf" in schema


def test_construct_json_schema_returns_one_kind_when_asked() -> None:
    schema = construct_json_schema(kind="SubClassOf")

    assert schema["title"] == "SubClassOf"
    assert "uid" in schema["properties"]
    assert "oneOf" not in schema


def test_construct_json_schema_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="Unknown construct kind 'Bogus'"):
        construct_json_schema(kind="Bogus")
