import os
import platform
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
