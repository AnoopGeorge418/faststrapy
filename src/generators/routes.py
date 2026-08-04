from pathlib import Path

from src.generators.fs_utils import write_file
from src.generators.registry import register_generator
from src.schemas.project_config import ProjectConfigSchema
from src.utils.jinja_env import render_template


@register_generator("health route", order=50)
def generate_routes(base_path: Path, config: ProjectConfigSchema) -> None:
    path_name = config.default_config.path_name
    write_file(
        base_path / path_name / "modules" / "routes" / "health_route.py",
        render_template("health_route.py.jinja"),
    )
