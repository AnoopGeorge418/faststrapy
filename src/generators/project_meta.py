from pathlib import Path

from src.generators.fs_utils import write_file
from src.generators.registry import register_generator
from src.schemas.project_config import ProjectConfigSchema

GITIGNORE = """\
__pycache__/
*.py[cod]
.venv/
venv/
.env
*.db
logs/
.pytest_cache/
.mypy_cache/
dist/
build/
*.egg-info/
"""


@register_generator("project metadata", order=5)
def generate_meta(base_path: Path, config: ProjectConfigSchema) -> None:
    pre = config.pre_config
    default = config.default_config
    base_path.mkdir(parents=True, exist_ok=True)

    deps = ["fastapi[all]", "uvicorn", "pydantic-settings"]
    if default.use_orm and default.orm_name == "sqlalchemy":
        deps.append("sqlalchemy")
    if default.use_database and default.database_name == "postgres":
        deps.append("asyncpg" if default.database_type == "async" else "psycopg2-binary")
    if default.use_alembic:
        deps.append("alembic")
    if default.use_black:
        deps.append("black")

    deps_block = "\n".join(f'    "{d}",' for d in deps)
    pyproject = f'''[project]
name = "{pre.project_name}"
version = "0.1.0"
description = "A FastAPI project scaffolded with faststrapy."
readme = "README.md"
requires-python = ">={pre.python_version}"
dependencies = [
{deps_block}
]
'''
    write_file(base_path / "pyproject.toml", pyproject)
    write_file(base_path / ".python-version", f"{pre.python_version}\n")
    write_file(base_path / ".gitignore", GITIGNORE)
    write_file(
        base_path / "README.md",
        f"# {pre.project_name}\n\nScaffolded with [faststrapy](https://github.com/AnoopGeorge418/faststrapy).\n\n"
        f"## Run\n\n```bash\nuv sync\nuv run main.py\n```\n",
    )
