from pathlib import Path


def write_file(path: Path, content: str) -> None:
    """Create parent dirs if needed and write content, overwriting if present."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def touch_init(path: Path) -> None:
    """Create an empty __init__.py at `path` (a directory)."""

    path.mkdir(parents=True, exist_ok=True)
    (path / "__init__.py").touch(exist_ok=True)
