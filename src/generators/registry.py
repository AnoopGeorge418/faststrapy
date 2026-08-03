from pathlib import Path

from src.schemas.project_config import ProjectConfigSchema
from src.schemas.registry_schema import ConditionFn, GeneratorEntrySchema, GeneratorFn


class GenerateFastApiProjectTree:
    """
        Decorator-based generator registry.
        
        A "generator" is a pure file-writer: given the built ProjectConfigSchema and
        an output directory, it decides whether it should run (via `condition_fn`)
        and if so, writes exactly one logical unit of the project tree (a file, or
        a small related group of files).
        
        Generators do NOT:
            - run subprocesses
            - install packages
            - touch git / uv / alembic CLIs
        That is postgen's job, which always runs strictly after every generator
        has finished.
    """

    def __init__(self) -> None:
        self.GENERATOR_REGISTRY: list[GeneratorEntrySchema] = []

    def register_generators(self, condition_fn: ConditionFn, order: int = 0):
        """
            Decorator to register a generator function.
    
            `condition_fn` receives the full ProjectConfigSchema and returns True if
            this generator should run for the current project.
            `order` controls execution order for generators whose output depends on
            another generator's output (lower runs first). Most generators write
            independent files and can share the default order=0.
        """

        def decorator(fn: GeneratorFn) -> GeneratorFn:
            self.GENERATOR_REGISTRY.append(
                GeneratorEntrySchema(
                    name=fn.__name__,
                    condition_fn=condition_fn,
                    generator_fn=fn,
                    order=order,
                )
            )

            return fn

        return decorator
    

    def run_generators(self, cfg: ProjectConfigSchema, output_dir: Path) -> list[str]:
        """Run every registered generator whose condition passes.
    
        Returns the list of generator names that actually ran, in execution
        order — useful for logging / --dry-run reporting.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
    
        ran: list[str] = []
        ordered_entries = sorted(self.GENERATOR_REGISTRY, key=lambda e: e.order)
    
        for entry in ordered_entries:
            if entry.condition_fn(cfg):
                entry.generator_fn(cfg, output_dir)
                ran.append(entry.name)
    
        return ran


    
    
