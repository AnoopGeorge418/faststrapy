"""Generator registry + all generator modules.

Importing this package has the side effect of registering every generator
(each module below decorates its function with @register_generator, which
appends it to the shared registry). `run_generators` is the single public
entrypoint the CLI calls once a ProjectConfigSchema is ready.
"""

from pathlib import Path

from faststrapy.generators.registry import registry
from faststrapy.schemas.project_config import ProjectConfigSchema

# Importing for registration side-effects (order doesn't matter here - the
# registry itself sorts by each generator's `order` before running).
from faststrapy.generators import (  # noqa: F401,E402
    alembic_gen,
    core_config,
    core_database,
    docker_gen,
    entrypoint,
    logging_gen,
    project_meta,
    routes,
    structure,
)


def run_generators(base_path: Path, config: ProjectConfigSchema) -> None:
    """Run every registered generator, in order, against `base_path`."""

    registry.run_all(base_path, config)
