from pydantic import BaseModel

from typing import Callable

from pathlib import Path

from src.schemas.project_config import ProjectConfigSchema

ConditionFn = Callable[[ProjectConfigSchema], bool]
GeneratorFn = Callable[[ProjectConfigSchema, Path], None]

class GeneratorEntrySchema(BaseModel):
    name: str
    condition_fn: ConditionFn
    generator_fn: GeneratorFn
    order: int = 0
