from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# trim_blocks/lstrip_blocks keep `{% if %}` control lines from leaking blank
# lines or stray indentation into the rendered Python files.
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


def render_template(template_name: str, **context) -> str:
    """Render a .jinja template from src/templates/ with the given context."""

    template = jinja_env.get_template(template_name)
    return template.render(**context)

