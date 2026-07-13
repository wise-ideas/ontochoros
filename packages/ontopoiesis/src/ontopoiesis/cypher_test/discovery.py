from __future__ import annotations

from pathlib import Path

ERROR_CYPHER_FILE_PATTERNS = (
    "test_*.cypher",
    "*_test.cypher",
)

WARNING_CYPHER_FILE_PATTERNS = (
    "warn_*.cypher",
    "*_warn.cypher",
)

DEFAULT_CYPHER_FILE_PATTERNS = ERROR_CYPHER_FILE_PATTERNS + WARNING_CYPHER_FILE_PATTERNS


def resolve_cypher_tests(tests_paths: list[Path] | None) -> list[Path]:
    targets = tests_paths or [Path("tests")]
    matches: list[Path] = []
    seen: set[Path] = set()
    for target in targets:
        for path in resolve_cypher_target(target):
            if path not in seen:
                seen.add(path)
                matches.append(path)
    return matches


def resolve_cypher_target(target: Path) -> list[Path]:
    if target.is_file() and target.suffix == ".cypher":
        return [target]
    if target.is_dir():
        return [path for path in sorted(target.rglob("*.cypher")) if matches_cypher_pattern(path)]
    return []


def matches_cypher_pattern(path: Path) -> bool:
    return any(path.match(pattern) for pattern in DEFAULT_CYPHER_FILE_PATTERNS)


def is_warning_cypher_path(path: Path) -> bool:
    return any(path.match(pattern) for pattern in WARNING_CYPHER_FILE_PATTERNS)
