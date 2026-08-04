import shutil
import subprocess
from pathlib import Path

from src.postgen.registry import register_postgen
from src.schemas.project_config import ProjectConfigSchema


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


@register_postgen("git init", order=10)
def git_init(base_path: Path, config: ProjectConfigSchema) -> None:
    if not shutil.which("git"):
        raise RuntimeError("git not found on PATH")
    _run(["git", "init"], cwd=base_path)
    _run(["git", "add", "."], cwd=base_path)
    _run(["git", "commit", "-m", "chore: scaffold project with faststrapy"], cwd=base_path)


@register_postgen("dependency install (uv sync)", order=20)
def uv_sync(base_path: Path, config: ProjectConfigSchema) -> None:
    if shutil.which("uv"):
        _run(["uv", "sync"], cwd=base_path)
        return
    raise RuntimeError("uv not found on PATH - run `uv sync` yourself once it's installed")


@register_postgen("format with black", order=30)
def run_black(base_path: Path, config: ProjectConfigSchema) -> None:
    if not config.default_config.use_black:
        return
    if shutil.which("uv"):
        _run(["uv", "run", "black", "."], cwd=base_path)
    elif shutil.which("black"):
        _run(["black", "."], cwd=base_path)
    else:
        raise RuntimeError("black not available - skipping formatting")

