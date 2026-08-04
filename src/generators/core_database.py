from pathlib import Path

from src.generators.fs_utils import write_file
from src.generators.registry import register_generator
from src.schemas.project_config import ProjectConfigSchema
from src.utils.jinja_env import render_template


@register_generator("database layer", order=30)
def generate_database(base_path: Path, config: ProjectConfigSchema) -> None:
    default = config.default_config
    if not default.use_database:
        return

    path_name = default.path_name
    db_dir = base_path / path_name / "core" / "database"

    ctx = {
        "path_name": path_name,
        "database_type": default.database_type,
        "database_host": default.database_host,
    }

    write_file(db_dir / "base.py", render_template("base.py.jinja"))
    write_file(db_dir / "connection.py", render_template("connection.py.jinja", **ctx))

    if default.database_type == "async":
        write_file(db_dir / "async_session.py", render_template("async_session.py.jinja", path_name=path_name))
    else:
        write_file(db_dir / "sync_session.py", render_template("sync_session.py.jinja", path_name=path_name))

    write_file(
        db_dir / "dependency.py",
        render_template("dependency.py.jinja", path_name=path_name, database_type=default.database_type),
    )
    write_file(db_dir / "module_registry.py", render_template("model_registry.py.jinja"))
