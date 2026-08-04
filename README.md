# faststrapy

A CLI tool to scaffold production-ready FastAPI projects instantly — inspired by `create-next-app`, powered by Jinja2 templates and interactive prompts.

Answer a handful of prompts (or pass flags and skip them entirely) and get a working FastAPI project: settings management, an optional SQLAlchemy + Alembic database layer, structured logging, a health-check route, `git init`, dependency install, and code formatting — all done for you.

```
$ faststrapy create-app
----------------------------------------------------
Generating `my-service` at /home/anoop/my-service
  → project metadata
  → project structure
  → settings + .env
  → database layer
  → logger
  → health route
  → main.py entrypoint
  → alembic
Running post-generation steps...
  → git init
  → ensure uv installed
  → dependency install (uv sync)
  → format with black
----------------------------------------------------
Done. Next steps:
----------------------------------------------------
  cd /home/anoop/my-service

  # activate the virtual environment uv created
  # (optional — `uv run` below works without activating)
  # Windows (cmd):        .venv\Scripts\activate
  # Windows (PowerShell): .venv\Scripts\Activate.ps1
  # macOS / Linux:        source .venv/bin/activate

  # run the project (from the project root)
  uv run python -m app.main

  # once it's running:
  http://127.0.0.1:8000
  http://127.0.0.1:8000/docs   (interactive Swagger UI)
  http://127.0.0.1:8000/redoc  (ReDoc API reference)
----------------------------------------------------
```

---

## Table of contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [CLI reference](#cli-reference)
- [What gets generated](#what-gets-generated)
- [How the prompts work](#how-the-prompts-work)
- [Post-generation steps](#post-generation-steps)
- [Running the generated project](#running-the-generated-project)
- [Project architecture (for contributors)](#project-architecture-for-contributors)
- [Contributing](#contributing)
- [Roadmap / known limitations](#roadmap--known-limitations)
- [License](#license)

---

## Requirements

- Python **3.10+** (the generated projects default to 3.11, configurable per-project down to 3.10 during the prompts)
- [`uv`](https://docs.astral.sh/uv/) — not strictly required to install faststrapy itself, but the post-generation step uses it to install the new project's dependencies. If it's missing, faststrapy installs it for you automatically (see [Post-generation steps](#post-generation-steps)).
- `git` — used for the automatic `git init` + first commit after scaffolding. Not required to run faststrapy itself, but that step is skipped with a warning if git isn't on `PATH`.

## Installation

```bash
# with uv (recommended)
uv tool install faststrapy
faststrapy create-app

# uv add faststrapy

# or run it once without installing, always pulling the latest version
uvx faststrapy create-app

# or with plain pip
pip install faststrapy
```

Once installed, the `faststrapy` command is on your `PATH`. There's no separate "run" step and no npm-style `@latest` suffix on individual commands — `uv add` / `pip install` pin the version at install time, and `faststrapy create-app` always runs whichever version you currently have installed. Upgrade with `uv add faststrapy --upgrade` or `pip install -U faststrapy`.

## Quick start

**Fully interactive** — no flags, faststrapy asks you everything (project name, framework, Python version, and whether to use the recommended defaults or customize every option):

```bash
faststrapy create-app
```

**Non-interactive** — pass any flag and all prompts are skipped; anything you don't pass falls back to a recommended default:

```bash
faststrapy create-app --project-name my-service --python 3.12 --sync-type async
```

**Scaffold into a specific directory:**

```bash
faststrapy create-app --project-name my-service --path ./services/my-service
```

**Skip git init / uv sync / black formatting** (just generate the files):

```bash
faststrapy create-app --project-name my-service --skip-postgen
```

## CLI reference

### `faststrapy create-app`

| Flag | Type | Description |
|---|---|---|
| `--project-name` | `str` | Name of the project. Also becomes the output folder name if `--path` isn't given, and the default `.env` variable prefix. |
| `--template` | `str` | Framework to scaffold. Currently only `fastapi` is implemented (see [Roadmap](#roadmap--known-limitations)). |
| `--python` | `float` | Target Python version for the generated project, e.g. `3.12`. |
| `--sync-type` | `str` | `sync` or `async` — controls both the database session style and the Alembic migration engine mode. |
| `--path` | `str` | Output directory. Defaults to `./<project-name>` in the current working directory. |
| `--skip-postgen` | flag | Skip `git init`, the `uv`/`uv sync` step, and Black formatting. Just write the files. |

Passing **any** of `--project-name`, `--template`, `--python`, `--sync-type`, or `--path` skips the interactive prompts entirely for that run — faststrapy fills in the rest with the recommended defaults (see [`_default_prompt_config`](faststrapy/prompts.py)). Pass none of them and you get the full interactive flow, including the "customize every option" path.

### `faststrapy logs`

```bash
faststrapy logs [--upgrade] [--downgrade]
```

Reports where a generated project's logs are configured to go (file vs. database), based on the `use_logs` / `save_logs_db` choices made at scaffold time.

## What gets generated

A default run (recommended settings, database + Alembic + logging + Black all enabled) produces:

```
my-service/
├── app/                        # ← everything lives here, not the project root
│   ├── __init__.py
│   ├── main.py                 #    FastAPI() app instance + entrypoint
│   ├── core/
│   │   ├── config/
│   │   │   └── settings.py     #    pydantic-settings Settings, reads .env
│   │   ├── database/           #    only if a database was selected
│   │   │   ├── base.py
│   │   │   ├── connection.py
│   │   │   ├── async_session.py    #  (or sync_session.py)
│   │   │   ├── dependency.py
│   │   │   └── module_registry.py
│   │   └── log/                #    only if logging was enabled
│   │       └── logger.py
│   ├── middlewares/
│   ├── utils/
│   └── modules/
│       ├── routes/
│       │   └── health_route.py #    GET /health, always generated
│       └── models/             #    only if a database was selected
├── alembic/                    #    only if Alembic was enabled
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── .env                        #    real values, gitignored
├── .env.example                #    same keys, committed
├── .gitignore
├── .python-version
├── pyproject.toml              #    dependencies resolved from your choices
├── requirements.txt            #    same deps, plain pip-installable format
└── README.md
```

Notes on a few of the choices baked into this layout:

- **`main.py` lives inside `app/`, not the project root.** The app is meant to be run as a module — `uv run python -m app.main` — which keeps `app.core...`-style absolute imports working correctly. Running it as a bare script (`python app/main.py`) would break those imports, since Python only adds the script's own directory to `sys.path`, not the project root.
- **Both `pyproject.toml` and `requirements.txt` are generated**, with matching dependency lists, so the project is installable either the `uv`/PEP 621 way or the classic `pip install -r requirements.txt` way.
- **`SERVER_PATH` in `.env`** is set to `app.main:app` (or `<your-folder-name>.main:app` if you renamed the holder folder) — this is the import string `uvicorn.run()` uses internally, and it's kept in sync with wherever `main.py` actually is.

## How the prompts work

1. **Pre-config** — project name, framework (`fastapi`; `flask`/`django` are recognized but not yet implemented — see [Roadmap](#roadmap--known-limitations)), Python version, and whether the app's code should live inside a subfolder (default: yes, `app/`).
2. You're then asked: **use the recommended defaults, or customize?**
   - **Recommended defaults**: Pydantic ✓, SQLAlchemy ORM ✓, Postgres (both local + Neon-ready) ✓, async DB access, Alembic ✓ (async), logging ✓ (console only), Black ✓.
   - **Customize**: one prompt per option — database on/off, which database, sync vs async, ORM on/off, env var prefix, Alembic on/off, logging on/off (and whether to persist to a file), Black on/off.

All of this is captured in [`ProjectConfigSchema`](faststrapy/schemas/project_config.py) (`PreConfig` + `DefaultConfig`), which is what every generator function receives.

## Post-generation steps

After the files are written, faststrapy runs (unless `--skip-postgen`):

1. **`git init`** — initializes a repo and creates the first commit (`chore: scaffold project with faststrapy`). Skipped with a warning if `git` isn't installed, or if your global `git` identity (`user.name`/`user.email`) isn't configured yet — the commit will fail but nothing else is affected.
2. **`uv` auto-install** — if `uv` isn't already on your `PATH`, faststrapy runs the official installer for your OS (the `curl | sh` one-liner on macOS/Linux, the `irm | iex` one on Windows) so the next step can succeed. This is best-effort: if it fails (offline, restricted permissions, unsupported shell), you get a one-line notice and the run continues — nothing crashes.
3. **`uv sync`** — installs the generated project's dependencies into a fresh `.venv`.
4. **Black formatting** — if you kept Black enabled, the generated code is formatted in place, pinned to the project's target Python version.

Every post-generation step is independently best-effort: if one fails, you get a `⚠ skipped (<reason>)` line and the rest still run. Nothing about a failed post-gen step blocks the "Done" summary at the end.

## Running the generated project

```bash
cd my-service

# optional — uv run works without activating a venv at all
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows (cmd)
.venv\Scripts\Activate.ps1       # Windows (PowerShell)

uv run python -m app.main
```

Then visit:

- `http://127.0.0.1:8000` — the app
- `http://127.0.0.1:8000/docs` — Swagger UI
- `http://127.0.0.1:8000/redoc` — ReDoc

Host, port, and reload behavior are all controlled by the generated `.env` (`SERVER_HOST`, `SERVER_PORT`, `SERVER_RELOAD`) via `app/core/config/settings.py`.

---

## Project architecture (for contributors)

faststrapy has three moving pieces, each with its own registry pattern:

```
faststrapy/
├── main.py                # Typer app entrypoint — registers sub_command
├── prompts.py              # All interactive prompt logic (FaststrapyPrompts)
├── schemas/
│   └── project_config.py   # PreConfig, DefaultConfig, ProjectConfigSchema — the
│                            # single object passed to every generator/postgen step
├── configs/
│   └── commands.py         # `create-app` and `logs` Typer commands; wires
│                            # prompts → generators → postgen → summary output
├── generators/              # Each file writes one slice of the new project
│   ├── registry.py          #  @register_generator("name", order=N) decorator
│   ├── structure.py         #  order=10  — folder skeleton + __init__.py files
│   ├── project_meta.py      #  order=5   — pyproject.toml, requirements.txt, .gitignore, README
│   ├── core_config.py       #  order=20  — settings.py, .env, .env.example
│   ├── core_database.py     #  order=30  — database layer (conditional)
│   ├── logging_gen.py       #  order=40  — logger.py (conditional)
│   ├── routes.py             #  order=50  — health_route.py
│   ├── entrypoint.py        #  order=60  — main.py
│   ├── alembic_gen.py       #  order=70  — alembic/ (conditional)
│   └── fs_utils.py          #  write_file() / touch_init() helpers
├── postgen/                  # Runs after files exist on disk
│   ├── registry.py          #  @register_postgen("name", order=N), catches
│                            #  exceptions per-step (best-effort by design)
│   └── actions.py           #  git init → ensure uv installed → uv sync → black
├── templates/                # .jinja templates rendered by the generators
│   └── *.py.jinja
└── utils/
    └── jinja_env.py          # Environment + render_template()
```

**How the registries work:** a generator (or postgen step) is just a function decorated with `@register_generator("human readable name", order=N)`. `run_generators()` / `run_postgen()` sort by `order` and run them in that sequence, printing the name as they go. Lower `order` runs first. There's no other wiring needed — importing the module (already done for you in `generators/__init__.py` / `postgen/__init__.py`) registers it.

### Adding a new generator

1. Create `faststrapy/generators/your_thing.py`.
2. Write a function `def generate_your_thing(base_path: Path, config: ProjectConfigSchema) -> None:`, decorated with `@register_generator("your thing", order=N)`. Pick `N` based on where it needs to run relative to the existing steps (e.g. after `structure` at 10, before `entrypoint` at 60 if it needs to exist before `main.py` references it).
3. If it's conditional (like the database layer), guard it: `if not config.default_config.<your_flag>: return`.
4. If it writes a new field, add it to `DefaultConfig` in `schemas/project_config.py` first, and wire a prompt for it in `prompts.py` (both the customize path *and*, if it should have a sensible default, `_default_prompt_config`).
5. Add the import to `faststrapy/generators/__init__.py`'s import list so the decorator actually runs.
6. If it renders a template, add the `.jinja` file under `faststrapy/templates/` and call `render_template("your_thing.py.jinja", **ctx)`.

### Adding a new postgen step

Same pattern in `faststrapy/postgen/actions.py`, decorated with `@register_postgen("name", order=N)`. Steps here are expected to shell out (`git`, `uv`, `black`, etc.) — raise a plain `RuntimeError` with a clear message on failure; the registry catches it and prints `⚠ skipped (<message>)` without stopping the rest of the run. Don't add a `try/except` inside your own step unless you need to do something *other* than fail — that's already handled centrally.

### Files you'll typically touch

| Change you want to make | File(s) |
|---|---|
| New scaffolding option / prompt | `schemas/project_config.py`, `prompts.py`, the relevant generator |
| New file type in generated projects | New file in `generators/`, new `.jinja` in `templates/` |
| Change what recommended defaults are | `prompts.py` → `_default_prompt_config` |
| Change CLI flags on `create-app` | `configs/commands.py` |
| New post-generation shell step | `postgen/actions.py` |
| Fix/change a generated file's content | The relevant `.jinja` file in `templates/` — **not** a `.py` file, these are text templates |

### Files to be careful changing (or avoid changing without discussion)

- **`pyproject.toml`** `[project.scripts]` and `[build-system]` — this is what makes `pip install faststrapy` produce a working `faststrapy` command at all. Breaking the entry point (`faststrapy.main:app`) or the `packages = ["faststrapy"]` wheel config breaks every install.
- **The `faststrapy/` package name itself** — this must match the PyPI project name and the console-script entry point. Don't rename or nest it further without updating `pyproject.toml` to match.
- **`generators/registry.py` / `postgen/registry.py`** — the ordering/execution engine both generator sets rely on. Changing its behavior (e.g. making generator failures best-effort like postgen's) is a real design decision, not a small tweak — raise it in an issue/PR description rather than changing it silently.
- **`SERVER_PATH` in `templates/env.py.jinja`** and where `entrypoint.py` writes `main.py` — these two have to agree with each other (see [What gets generated](#what-gets-generated)). If you move `main.py`'s output location, update `SERVER_PATH` to match, and vice versa.
- **`templates/script_mako.py.jinja`** — despite the `.jinja` extension (for consistency with the rest of the folder), this is copied verbatim, not rendered through Jinja — it uses Mako's `${...}` syntax, consumed by Alembic itself at `alembic revision` time. Don't run it through `render_template()`.

## Contributing

1. **Fork the repo**, then clone your fork.
2. **Set up a dev environment:**
   ```bash
   uv sync
   uv pip install -e .
   ```
   This installs faststrapy in editable mode so `faststrapy create-app` (or `uv run faststrapy create-app`) reflects your local changes immediately.
3. **Branch naming** — prefix by intent, short and hyphenated:
   - `feature/<short-description>` — new generator, new prompt, new flag
   - `fix/<short-description>` — bug fixes
   - `docs/<short-description>` — README/docs-only changes
   - `chore/<short-description>` — packaging, CI, dependency bumps, refactors with no behavior change

   e.g. `feature/flask-template`, `fix/alembic-sync-mode`, `docs/contributing-section`.
4. **Commit messages** — [Conventional Commits](https://www.conventionalcommits.org/) style is preferred: `feat: add flask template support`, `fix: correct SERVER_PATH for renamed app folder`, `docs: expand CLI reference`. Not strictly enforced, but it's what the existing history follows and keeps changelogs generatable later.
5. **Test your change manually before opening a PR** — there's no automated test suite yet (see [Roadmap](#roadmap--known-limitations)), so the working smoke test is:
   ```bash
   uv run faststrapy create-app --project-name smoke-test --path /tmp/smoke-test
   cd /tmp/smoke-test
   uv run python -m app.main   # confirm it boots and /docs loads
   ```
   Run this with both the recommended-defaults path and, if your change touches a conditional generator (database/logging/alembic), the customize path with that option toggled off, to make sure nothing assumes it's always on.
6. **Open the PR against `main`**, describe what changed and why, and mention which generator/postgen `order` values (if any) you added or touched, since ordering bugs are the easiest thing to introduce silently.

### Reporting issues

Open a GitHub issue with: the exact `faststrapy create-app` command you ran (flags included), your OS and Python version, and the full output. If it's about the generated project rather than the CLI itself, include the relevant generated file.

## Roadmap / known limitations

- `--template flask` and `--template django` are recognized by the prompts but explicitly rejected as "still in progress" — only `fastapi` is implemented today.
- No automated test suite yet — contributions here are especially welcome (a good first one: a pytest suite that runs `create_app` programmatically against a temp dir for each generator combination and asserts the expected files exist).
- `faststrapy logs` currently only reports the configured log destination; it doesn't yet manage log files/DB rows for an existing project.
- The `uv` auto-install postgen step shells out to the official installer scripts (`astral.sh/uv/install.sh` / `.ps1`) at run time — if your network blocks that domain, the step fails gracefully but you'll need to install `uv` yourself.

## License

MIT — see [LICENSE](LICENSE).
