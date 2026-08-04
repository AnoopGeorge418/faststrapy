from typer import Typer

from faststrapy.configs.commands import sub_command

# Typer initilazation
app = Typer(
    name="faststrapy",
    add_completion=True,
    rich_markup_mode="rich",
    rich_help_panel="Utils and Configs",
    suggest_commands=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_short=True,
    context_settings={"help_option_names": ["-h", "--help"]}
)

# Registering sub commands
app.add_typer(sub_command)

if __name__ == "__main__":
    app()
