from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from src.schemas.project_config import ProjectConfigSchema

PostGenFunc = Callable[[Path, ProjectConfigSchema], None]


@dataclass
class _PostGenRegistry:
    """Same pattern as generators/registry.py, but for steps that run *after*
    the project files already exist on disk (shelling out to git, uv, etc).
    """

    _steps: list[tuple[str, int, PostGenFunc]] = field(default_factory=list)

    def register(self, name: str, order: int = 100):
        def decorator(fn: PostGenFunc) -> PostGenFunc:
            self._steps.append((name, order, fn))
            return fn
        return decorator

    def run_all(self, base_path: Path, config: ProjectConfigSchema) -> None:
        ordered = sorted(self._steps, key=lambda item: item[1])
        for name, _, fn in ordered:
            print(f"  → {name}")
            try:
                fn(base_path, config)
            except Exception as exc:  # noqa: BLE001 - post-gen steps are best-effort
                print(f"    ⚠ skipped ({exc})")


registry = _PostGenRegistry()
register_postgen = registry.register
