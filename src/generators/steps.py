"""
Concrete generator functions.

Each generator is a pure function: (ProjectConfigSchema, output_dir) -> None.
It renders exactly one template (or a small tightly-related group) and
writes it to disk. Nothing here touches subprocess, pip, uv, or git —
that's postgen's job.
"""

from pathlib import Path

from src.generators.jinja_env import render
from src.generators.registry import GenerateFastApiProjectTree
from src.schemas.project_config import ProjectConfigSchema

generator = GenerateFastApiProjectTree()

def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---- Always-run generators (no condition needed beyond "always True") ----


@generator.register_generators(lambda cfg: True, order=0)
def generate_pyproject(cfg: ProjectConfigSchema, output_dir: Path) -> None:
    content = render("pyproject.toml.jinja", cfg)
    _write(output_dir / "pyproject.toml", content)


@generator.register_generators(lambda cfg: True, order=0)
def generate_readme(cfg: ProjectConfigSchema, output_dir: Path) -> None:
    content = render("README.md.jinja", cfg)
    _write(output_dir / "README.md", content)


@generator.register_generators(lambda cfg: True, order=0)
def generate_gitignore(cfg: ProjectConfigSchema, output_dir: Path) -> None:
    content = render("gitignore.jinja", cfg)
    _write(output_dir / ".gitignore", content)


@generator.register_generators(lambda cfg: True, order=1)
def generate_main(cfg: ProjectConfigSchema, output_dir: Path) -> None:
    content = render("main.py.jinja", cfg)
    _write(output_dir / "src" / "main.py", content)
    _write(output_dir / "src" / "__init__.py", "")


# ---- Conditional generators, gated on DefaultConfig fields ----


@generator.register_generators(lambda cfg: cfg.default_config.use_pydantic, order=1)
def generate_config(cfg: ProjectConfigSchema, output_dir: Path) -> None:
    content = render("config.py.jinja", cfg)
    _write(output_dir / "src" / "core" / "config.py", content)
    _write(output_dir / "src" / "core" / "__init__.py", "")


@generator.register_generators(
    lambda cfg: cfg.default_config.use_orm and cfg.default_config.orm_name == "sqlalchemy",
    order=2,  # runs after config.py exists, since database.py imports settings
)
def generate_database(cfg: ProjectConfigSchema, output_dir: Path) -> None:
    content = render("database.py.jinja", cfg)
    _write(output_dir / "src" / "core" / "database.py", content)


@generator.register_generators(lambda cfg: cfg.default_config.use_database, order=1)
def generate_env_file(cfg: ProjectConfigSchema, output_dir: Path) -> None:
    content = render("env.jinja", cfg)
    _write(output_dir / ".env", content)


@generator.register_generators(lambda cfg: cfg.default_config.use_logs, order=1)
def generate_logging_config(cfg: ProjectConfigSchema, output_dir: Path) -> None:
    content = render("logging_config.py.jinja", cfg)
    _write(output_dir / "src" / "core" / "logging_config.py", content)


@generator.register_generators(lambda cfg: cfg.default_config.save_logs_db, order=1)
def generate_logs_dir(cfg: ProjectConfigSchema, output_dir: Path) -> None:
    # Just needs to exist so FileHandler("logs/app.log") doesn't crash on first run
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    (logs_dir / ".gitkeep").write_text("")
