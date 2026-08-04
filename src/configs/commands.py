from pathlib import Path
from typing import Optional

from typer import Typer

from src.generators import run_generators
from src.postgen import run_postgen
from src.prompts import FaststrapyPrompts
from src.schemas.project_config import PreConfig, ProjectConfigSchema

# typer instance for created sub command
sub_command = Typer()


@sub_command.command(help="Create app using any or all of these tags --project_name, --template, --python, --type, --path")
def create_app(
        project_name: Optional[str] = None,
        template: Optional[str] = None,
        python: Optional[float] = None,
        sync_type: Optional[str] = None,
        path: Optional[str] = None,
        skip_postgen: bool = False,
    ):
    """Creates a faststrapy app.

    If any flag is passed, prompts are skipped entirely for that field and
    recommended defaults fill in the rest. With zero flags, falls back to
    the full interactive flow.
    """

    if any([project_name, template, python, sync_type, path]):
        # Non-interactive: build straight from CLI args + recommended
        # defaults. Never touches the prompt functions.
        resolved_name = project_name or "faststrapy-app"

        pre_config = PreConfig(
            project_name=resolved_name,
            framework=template or "fastapi",
            python_version=python or 3.11,
            default_settings=True,
            holder_folder="app",
        )
        default_config = FaststrapyPrompts._default_prompt_config(path_name=pre_config.holder_folder)
        default_config.env_prefix = pre_config.project_name.upper()
        if sync_type:
            default_config.database_type = sync_type
            default_config.alembic_type = sync_type

        config = ProjectConfigSchema(pre_config=pre_config, default_config=default_config)
    else:
        # Nothing passed at all -> genuinely interactive
        config = FaststrapyPrompts.build_project_config()

    output_root = Path(path) if path else Path.cwd() / config.pre_config.project_name

    print("----------------------------------------------------")
    print(f"Generating `{config.pre_config.project_name}` at {output_root}")
    run_generators(output_root, config)

    if not skip_postgen:
        print("Running post-generation steps...")
        run_postgen(output_root, config)

    path_name = config.default_config.path_name

    print("----------------------------------------------------")
    print("Done. Next steps:")
    print("----------------------------------------------------")
    print(f"  cd {output_root}")
    print()
    print("  # activate the virtual environment uv created")
    print("  # (optional — `uv run` below works without activating)")
    print("  # Windows (cmd):        .venv\\Scripts\\activate")
    print("  # Windows (PowerShell): .venv\\Scripts\\Activate.ps1")
    print("  # macOS / Linux:        source .venv/bin/activate")
    print()
    print(f"  # run the project (from the project root)")
    print(f"  uv run python -m {path_name}.main")
    print()
    print("  # once it's running:")
    print("  http://127.0.0.1:8000")
    print("  http://127.0.0.1:8000/api/v1/health-route   (Health Route)")
    print("  http://127.0.0.1:8000/docs   (interactive Swagger UI)")
    print("  http://127.0.0.1:8000/redoc  (ReDoc API reference)")
    print("----------------------------------------------------")


@sub_command.command(help="logs everything based on level to db if --upgrade used else to file if --downgrade is used")
def logs(upgrade: bool = False, downgrade: bool = True):
    if not upgrade:
        print("Logs are being saved into file in root `logs` folder.")
    if not downgrade:
        print("Logs are being saved into database.")
