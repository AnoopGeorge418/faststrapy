from pathlib import Path

from src.generators.fs_utils import touch_init
from src.generators.registry import register_generator
from src.schemas.project_config import ProjectConfigSchema


@register_generator("project structure", order=10)
def generate_structure(base_path: Path, config: ProjectConfigSchema) -> None:
    """Lays down the package skeleton (all the __init__.py-bearing folders)
    that the rest of the generators write into.
    """

    path_name = config.default_config.path_name
    app_root = base_path / path_name

    touch_init(app_root)
    touch_init(app_root / "core")
    touch_init(app_root / "core" / "config")
    touch_init(app_root / "middlewares")
    touch_init(app_root / "utils")
    touch_init(app_root / "modules")
    touch_init(app_root / "modules" / "routes")

    if config.default_config.use_database:
        touch_init(app_root / "core" / "database")
        touch_init(app_root / "modules" / "models")

    if config.default_config.use_logs:
        touch_init(app_root / "core" / "log")
