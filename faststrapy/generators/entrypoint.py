from pathlib import Path

from faststrapy.generators.fs_utils import write_file
from faststrapy.generators.registry import register_generator
from faststrapy.schemas.project_config import ProjectConfigSchema
from faststrapy.utils.jinja_env import render_template


@register_generator("main.py entrypoint", order=60)
def generate_entrypoint(base_path: Path, config: ProjectConfigSchema) -> None:
    ctx = {
        "project_name": config.pre_config.project_name,
        "path_name": config.default_config.path_name,
    }
    write_file(base_path / ctx["path_name"] / "main.py", render_template("main.py.jinja", **ctx))
