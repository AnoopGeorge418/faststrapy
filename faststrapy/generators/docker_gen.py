from pathlib import Path

from faststrapy.generators.fs_utils import write_file
from faststrapy.generators.registry import register_generator
from faststrapy.schemas.project_config import ProjectConfigSchema
from faststrapy.utils.jinja_env import render_template


@register_generator("docker config", order=80)
def generate_docker(base_path: Path, config: ProjectConfigSchema) -> None:
    default = config.default_config
    if not default.use_docker:
        return

    pre = config.pre_config
    ctx = {
        "project_name": pre.project_name,
        "python_version": pre.python_version,
        "path_name": default.path_name,
        "use_database": default.use_database,
        "database_name": default.database_name,
        "database_host": default.database_host,
    }

    write_file(base_path / "Dockerfile", render_template("Dockerfile.jinja", **ctx))
    write_file(base_path / ".dockerignore", render_template("dockerignore.jinja", **ctx))
    write_file(base_path / "docker-compose.yml", render_template("docker_compose.jinja", **ctx))
