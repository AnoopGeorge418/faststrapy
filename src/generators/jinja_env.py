from importlib.resources import files

from jinja2 import Environment, FileSystemLoader

_env: Environment | None = None


def get_jinja_env() -> Environment:
    """
        Lazily build a single shared Jinja2 environment.

        Uses importlib.resources instead of a hardcoded relative path so this
        works identically whether faststrapy is run from source (`uv run`) or
        from an installed wheel (`uvx faststrapy`).
    """
    
    global _env
    if _env is None:
        template_dir = files("faststrapy").joinpath("templates")
        _env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
    return _env


def render(template_name: str, cfg) -> str:
    env = get_jinja_env()
    template = env.get_template(template_name)
    return template.render(pre_config=cfg.pre_config, default_config=cfg.default_config)
