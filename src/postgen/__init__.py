"""Post-generation steps (git init, uv sync, formatting), run after the
generator pipeline has written the project to disk.
"""

from pathlib import Path

from src.postgen.registry import registry
from src.schemas.project_config import ProjectConfigSchema

from src.postgen import actions  # noqa: F401  (registration side-effect)


def run_postgen(base_path: Path, config: ProjectConfigSchema) -> None:
    registry.run_all(base_path, config)
