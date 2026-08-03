from typing import Optional

from typer import Typer

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
    ):
    """Creates a faststrapy app.
        
    If any flag is passed, prompts are skipped entirely for that field and
    recommended defaults fill in the rest. With zero flags, falls back to
    the full interactive flow.
    """
    
    if any([project_name, template, python, sync_type, path]):
        # Non-interactive: build straight from CLI args + recommended
        # defaults. Never touches the prompt functions.
        pre_config = PreConfig(
            project_name=project_name or "faststrapy-app",
            framework=template or "fastapi",
            python_version=python or 3.11,
            default_settings=True,
        )
        default_config = FaststrapyPrompts._default_prompt_config()
        default_config.env_prefix = pre_config.project_name.upper()
        if sync_type:
            default_config.database_type = sync_type
            default_config.alembic_type = sync_type

        config = ProjectConfigSchema(pre_config=pre_config, default_config=default_config)
    else:
        # Nothing passed at all -> genuinely interactive
        config = FaststrapyPrompts.build_project_config()

    # TODO: pass `config` (and `path`, for output location) to the generator
    print(config)

@sub_command.command(help="logs everything based on level to db if --upgrade used else to file if --downgrade is used")
def logs(upgrade: bool = False, downgrade: bool = True):
    if not upgrade:
        print("Logs are being saved into file in root `logs` folder.")
    if not downgrade:
        print("Logs are being saved into database.")
        

