from pathlib import Path

from faststrapy.generators.fs_utils import write_file
from faststrapy.generators.registry import register_generator
from faststrapy.schemas.project_config import ProjectConfigSchema
from faststrapy.utils.jinja_env import render_template


@register_generator("logger", order=40)
def generate_logger(base_path: Path, config: ProjectConfigSchema) -> None:
    default = config.default_config
    if not default.use_logs:
        return

    path_name = default.path_name
    ctx = {
        "project_name": config.pre_config.project_name,
        "save_logs_db": default.save_logs_db,
    }
    write_file(base_path / path_name / "core" / "log" / "logger.py", render_template("logger.py.jinja", **ctx))
