from pathlib import Path

from src.generators.fs_utils import write_file
from src.generators.registry import register_generator
from src.schemas.project_config import ProjectConfigSchema
from src.utils.jinja_env import TEMPLATES_DIR, render_template


@register_generator("alembic", order=70)
def generate_alembic(base_path: Path, config: ProjectConfigSchema) -> None:
    default = config.default_config
    if not default.use_alembic:
        return

    path_name = default.path_name
    alembic_dir = base_path / "alembic"

    write_file(
        alembic_dir / "env.py",
        render_template("alembic_env.py.jinja", path_name=path_name, alembic_type=default.alembic_type),
    )
    write_file(base_path / "alembic.ini", render_template("alembic_ini.py.jinja", use_black=default.use_black))

    # script.py.mako uses Mako's ${...} syntax (consumed by alembic itself at
    # `alembic revision` time), so it's copied verbatim rather than rendered
    # through Jinja.
    mako_src = TEMPLATES_DIR / "script_mako.py.jinja"
    write_file(alembic_dir / "script.py.mako", mako_src.read_text(encoding="utf-8"))

    (alembic_dir / "versions").mkdir(parents=True, exist_ok=True)
    (alembic_dir / "versions" / ".gitkeep").touch(exist_ok=True)
