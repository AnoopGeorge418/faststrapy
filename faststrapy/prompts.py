from typer import prompt, confirm

from click import Choice

from faststrapy.schemas.project_config import DefaultConfig, PreConfig, ProjectConfigSchema


class FaststrapyPrompts:
    """Prompts that are used to generated project tree with base files and folders"""


    @staticmethod
    def _pre_config_prompts() -> PreConfig:
        project_name = prompt("Enter project Name").lower()

        print("----------------------------------------------------")

        supported_frameworks = ["fastapi", "flask", "django"]

        selected_framework = None
        while selected_framework not in supported_frameworks:
            choice = prompt(
                "Choose a framework",
                type=Choice(["fastapi", "flask", "django"]),
                default="fastapi"
            ).lower()

            if not choice in supported_frameworks:
                print(f"Unknown framework `{choice}` is not supported")
            elif choice in ("flask", "django"):
                print(f"`{choice}` framework support still in progress..")
            elif choice == "fastapi":
                selected_framework = choice

        while True:
            python_version_input = prompt("Select python version", default="3.11")
            try:
                python_version = float(python_version_input)
            except ValueError:
                print("Please enter a valid version number, e.g. 3.11")
                continue
            if 3.10 <= python_version <= 3.14:
                break
            print("Unsupported Python version.")


        default_settings = confirm("Do you want continue with recommended default settings", default=True)

        content_holder_folder = confirm("Do you want all the code to be inside app folder", default=True)
        if not content_holder_folder:
            content_holder_folder = prompt(
                "Enter the root folder name",
                default="app"
            )
        else:
            # confirm() returns True/False, not a folder name — normalize
            # to the actual default folder name when the user says "yes"
            content_holder_folder = "app"

        return PreConfig(
            project_name=project_name,
            framework=selected_framework,
            python_version=python_version,
            default_settings=default_settings,
            holder_folder=content_holder_folder
        )


    @staticmethod
    def _default_prompt_config(path_name: str) -> DefaultConfig:
        """The 'recommended defaults' path — no prompts, just sensible values."""

        return DefaultConfig(
            use_pydantic=True,
            use_orm=True,
            orm_name="sqlalchemy",
            use_database=True,
            database_name="postgres",
            database_type="async",
            database_host="both",
            env_prefix=None,
            use_alembic=True,
            alembic_type="async",
            use_logs=True,
            save_logs_db=False,
            use_black=True,
            use_docker=True,
            path_name=path_name
        )



    @staticmethod
    def _ask_customize_project_prompts(pre_config: PreConfig) -> ProjectConfigSchema:
        """The 'customize manually' path — asks one prompt per option."""

        print("----------------------------------------------------")
        print(f"Customizing project `{pre_config.project_name}`...")

        # custom prompts to configure project
        use_pydantic = True
        use_database = confirm("Use a database", default=True)

        database_name = None
        database_type = None
        database_host = None

        if use_database:
            database_name = prompt(
                "Choose a database",
                type=Choice(["postgres", "sqlite3"]),
                default="postgres"
            )
            database_type = prompt(
                "Sync or async db access?",
                type=Choice(["sync", "async"]),
                default="async"
            )

            if database_name == "postgres":
                database_host = prompt(
                    "Choose a database host",
                    type=Choice(["local", "neon", "both"]),
                    default="local"
                )

        # orm --> if database True
        use_orm = False
        orm_name = None

        if use_database:
            use_orm = confirm("Use an ORM?", default=True)
            if use_orm:
                orm_name = prompt(
                    "Choose ORM",
                    type=Choice(["SqlAlchemy", "DjangoORM"]),
                    default="SqlAlchemy"
                )
        else:
            print("Skipping ORM setup (no database selected).")

        env_prefix = prompt(
            "Environment variable prefix",
            default=pre_config.project_name.upper()
        )

        # alembic -- if orm and db --> True
        use_alembic = False
        alembic_type = None

        if use_orm and orm_name == "sqlalchemy" and use_database:
            use_alembic = confirm("Use Alembic for migrations?", default=True)
            if use_alembic:
                # Keep alembic's engine mode in sync with the DB access mode
                alembic_type = database_type

        use_logs = confirm("Set up logging?", default=True)
        save_logs_db = False

        if use_logs:
            save_logs_db = confirm("Persist logs to a file?", default=False)

        use_black = confirm("Use Black for formatting?", default=True)

        use_docker = confirm("Generate Docker config (Dockerfile, docker-compose.yml)?", default=True)


        default_config = DefaultConfig(
            use_pydantic=use_pydantic,
            use_orm=use_orm,
            orm_name=orm_name,
            use_database=use_database,
            database_name=database_name,
            database_type=database_type,
            database_host=database_host,
            env_prefix=env_prefix,
            use_alembic=use_alembic,
            alembic_type=alembic_type,
            use_logs=use_logs,
            save_logs_db=save_logs_db,
            use_black=use_black,
            use_docker=use_docker,
            path_name=pre_config.holder_folder,
        )

        return ProjectConfigSchema(pre_config=pre_config, default_config=default_config)

    @staticmethod
    def build_project_config() -> ProjectConfigSchema:
        pre_config = FaststrapyPrompts._pre_config_prompts()
        if pre_config.default_settings:
            # User said "yes" -> skips customization, use recommended defaults
            default_config = FaststrapyPrompts._default_prompt_config(
                path_name=pre_config.holder_folder
            )
            if default_config.env_prefix is None:
                default_config.env_prefix = pre_config.project_name.upper()

            return ProjectConfigSchema(
                pre_config=pre_config,
                default_config=default_config
            )
        else:
            # User said "no" -> ask for each option manually
            return FaststrapyPrompts._ask_customize_project_prompts(pre_config)

# if __name__ == "__main__":
#     config = FaststrapyPrompts.build_project_config()
#     print(config)
