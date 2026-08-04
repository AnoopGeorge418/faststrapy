import shutil
import subprocess
from pathlib import Path

from src.postgen.registry import register_postgen
from src.schemas.project_config import ProjectConfigSchema


def _run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(
            f"`{' '.join(cmd)}` exited {result.returncode}"
            + (f": {detail}" if detail else "")
        )


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

    # Pin --target-version explicitly instead of letting black infer it from
    # requires-python's open-ended ">=X" range, which can resolve to a newer
    # version than the interpreter actually running black understands.
    py = config.pre_config.python_version
    target = f"py{str(py).replace('.', '')}"
    cmd_tail = ["black", "--target-version", target, "."]

    if shutil.which("uv"):
        _run(["uv", "run"] + cmd_tail, cwd=base_path)
    elif shutil.which("black"):
        _run(cmd_tail, cwd=base_path)
    else:
        raise RuntimeError("black not available - skipping formatting")
