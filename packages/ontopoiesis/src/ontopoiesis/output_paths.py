from pathlib import Path


def default_lbug_output_path(input_path: Path) -> Path:
    return input_path.with_suffix(".lbug")


def default_owlxml_output_path(input_path: Path) -> Path:
    return input_path.with_suffix(".owx")
