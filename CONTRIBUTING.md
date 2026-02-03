# Contributing

## Setup
- Use Python 3.10+.
- Create and activate a virtual environment.
- Install dev dependencies:
  - `pip install -e .[dev]`
  - Add GUI extras when needed: `pip install -e .[gui]`

## Quality checks
- Lint: `ruff check .`
- Format: `ruff format .`
- Tests: `pytest -q`

## Pull requests
- Keep PRs small and focused.
- Explain what changed, why it changed, and how to test.
- Do not commit local data files (`v1/destinatarios.json`, `v2/data/destinatarios.json`, `.env`).
