from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from faststrapy.schemas.project_config import ProjectConfigSchema

GeneratorFunc = Callable[[Path, ProjectConfigSchema], None]


@dataclass
class _GeneratorRegistry:
    """Collects generator functions and runs them in a deterministic order.

    Generators register themselves via the `@register_generator(...)` decorator
    (see generators/__init__.py for the modules that use it). Each generator
    receives the resolved project root path and the full ProjectConfigSchema,
    and is responsible for writing its own slice of the project to disk.
    """

    _generators: list[tuple[str, int, GeneratorFunc]] = field(default_factory=list)

    def register(self, name: str, order: int = 100):
        def decorator(fn: GeneratorFunc) -> GeneratorFunc:
            self._generators.append((name, order, fn))
            return fn
        return decorator

    def run_all(self, base_path: Path, config: ProjectConfigSchema) -> None:
        ordered = sorted(self._generators, key=lambda item: item[1])
        for name, _, fn in ordered:
            print(f"  → {name}")
            fn(base_path, config)


registry = _GeneratorRegistry()
register_generator = registry.register
