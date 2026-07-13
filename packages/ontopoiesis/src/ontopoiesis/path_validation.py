from pathlib import Path

import typer


def require_lbug_input(path: Path, *, parameter_name: str = "input_path") -> Path:
    if path.suffix.lower() != ".lbug":
        raise typer.BadParameter(
            f"{parameter_name} must point to a .lbug graph database; "
            "use `build` first for ontology documents."
        )
    return path


def require_lbug_output(path: Path, *, parameter_name: str = "output_path") -> Path:
    if path.suffix.lower() != ".lbug":
        raise typer.BadParameter(f"{parameter_name} must use a .lbug file extension.")
    return path
