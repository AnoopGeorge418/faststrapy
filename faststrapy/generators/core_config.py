from pathlib import Path

from faststrapy.generators.fs_utils import write_file
from faststrapy.generators.registry import register_generator
from faststrapy.schemas.project_config import ProjectConfigSchema
from faststrapy.utils.jinja_env import render_template


@register_generator("settings + .env", order=20)
def generate_settings(base_path: Path, config: ProjectConfigSchema) -> None:
    pre = config.pre_config
    default = config.default_config
    path_name = default.path_name

    ctx = {
        "env_prefix": default.env_prefix,
        "use_database": default.use_database,
    }
    settings_code = render_template("settings.py.jinja", **ctx)
    write_file(base_path / path_name / "core" / "config" / "settings.py", settings_code)

    env_ctx = {
        "env_prefix": default.env_prefix,
        "project_name": pre.project_name,
        "path_name": path_name,
        "use_database": default.use_database,
        "database_name": default.database_name,
        "database_type": default.database_type,
    }
    env_code = render_template("env.py.jinja", **env_ctx)
    write_file(base_path / ".env", env_code)
    write_file(base_path / ".env.example", env_code)
