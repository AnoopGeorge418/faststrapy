import os
import platform
import shutil
import subprocess
from pathlib import Path

from typer import confirm

from faststrapy.postgen.registry import register_postgen
from faststrapy.schemas.project_config import ProjectConfigSchema


def _run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(
            f"`{' '.join(cmd)}` exited {result.returncode}"
            + (f": {detail}" if detail else "")
        )


def _capture(cmd: list[str], cwd: Path) -> str:
    """Same as `_run`, but returns stdout instead of discarding it."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(
            f"`{' '.join(cmd)}` exited {result.returncode}"
            + (f": {detail}" if detail else "")
        )
    return result.stdout


@register_postgen("git init", order=10)
def git_init(base_path: Path, config: ProjectConfigSchema) -> None:
    if not shutil.which("git"):
        raise RuntimeError("git not found on PATH")

    # If the parent folder already has its own git repo (e.g. this project
    # was scaffolded inside an existing monorepo/workspace), don't nest a
    # second repo inside it without asking first.
    parent_git_exists = (base_path.parent / ".git").exists()

    if parent_git_exists:
        init_anyway = confirm(
            "A git repo already exists in the parent folder. "
            "Initialize a new one inside this project too?",
            default=False,
        )
        if not init_anyway:
            print("    Skipping git init - using the existing repo in the parent folder.")
            return

    _run(["git", "init"], cwd=base_path)
    _run(["git", "add", "."], cwd=base_path)
    _run(["git", "commit", "-m", "chore: scaffold project with faststrapy"], cwd=base_path)


@register_postgen("ensure uv installed", order=15)
def ensure_uv(base_path: Path, config: ProjectConfigSchema) -> None:
    """Installs `uv` globally via its official installer when it's missing,
    so a user without uv doesn't hit a hard failure on the next step.

    Best-effort and silent-on-success: if the install fails for any reason
    (offline, no shell access, restricted permissions, unsupported platform),
    this just raises a friendly RuntimeError - the postgen registry catches
    it, prints a one-line "skipped" notice, and the rest of the run
    continues undisturbed.
    """
    if shutil.which("uv"):
        return

    print("    `uv` not found - installing it now via the official installer...")

    system = platform.system()
    try:
        if system == "Windows":
            cmd = [
                "powershell",
                "-ExecutionPolicy", "ByPass",
                "-c", "irm https://astral.sh/uv/install.ps1 | iex",
            ]
        else:
            cmd = ["bash", "-c", "set -o pipefail; curl -LsSf https://astral.sh/uv/install.sh | sh"]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(detail or f"installer exited {result.returncode}")
    except Exception as exc:
        raise RuntimeError(
            f"couldn't auto-install uv ({exc}). Install it yourself from "
            "https://docs.astral.sh/uv/getting-started/installation/ then run `uv sync`"
        ) from exc

    if shutil.which("uv"):
        print("    `uv` installed successfully.")
        return

    # The installer writes to shell rc files, not this process's env, so a
    # fresh install is often invisible to `shutil.which` until the next
    # terminal session. Check the common install dirs and patch PATH for the
    # rest of this run so uv_sync (below) can still find it immediately.
    for candidate_dir in (Path.home() / ".local" / "bin", Path.home() / ".cargo" / "bin"):
        if (candidate_dir / "uv").exists():
            os.environ["PATH"] = f"{candidate_dir}{os.pathsep}{os.environ.get('PATH', '')}"
            break

    if shutil.which("uv"):
        print("    `uv` installed successfully.")
    else:
        raise RuntimeError("uv installed but not yet on PATH - restart your terminal, then run `uv sync`")


@register_postgen("dependency install (uv sync)", order=20)
def uv_sync(base_path: Path, config: ProjectConfigSchema) -> None:
    if shutil.which("uv"):
        _run(["uv", "sync"], cwd=base_path)
        return
    raise RuntimeError("uv not found on PATH - run `uv sync` yourself once it's installed")


@register_postgen("freeze requirements.txt", order=25)
def freeze_requirements(base_path: Path, config: ProjectConfigSchema) -> None:
    """Overwrites the hand-built requirements.txt (written at generation
    time, before any real install has happened) with the actual resolved
    versions from the synced .venv - same idea as `pip freeze`, but backed
    by `uv`'s resolver so the pins reflect what's really installed.

    Depends on `uv_sync` (order=20) having already created the .venv this
    run reads from - if that step failed or was skipped, this one falls
    back gracefully (best-effort, like every other postgen step) and the
    project keeps the generation-time requirements.txt instead.
    """
    if not shutil.which("uv"):
        raise RuntimeError("uv not found on PATH - keeping the generated requirements.txt")

    frozen = _capture(["uv", "pip", "freeze"], cwd=base_path)
    (base_path / "requirements.txt").write_text(frozen, encoding="utf-8")


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
