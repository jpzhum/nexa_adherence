# Contributing

## Setup

- Use Python 3.10+.
- Create and activate a virtual environment.
- Install dev dependencies:
  - `pip install -e ".[dev]"`
  - Add GUI extras when needed: `pip install -e ".[gui]"`

## Quality checks

- Lint: `ruff check .`
- Formatting: `ruff format --check .`
- Tests: `pytest -q`

## Pull requests

- Keep PRs small and focused.
- Explain what changed, why it changed, and how to test.
- Do not commit local data files, databases, logs, generated reports, recipient lists, or `.env`.
- Use only synthetic fixtures and reserved example values such as `user@example.com`.
- Do not change business rules solely to make a test pass; document and investigate the mismatch.
- Report security issues using the process in `SECURITY.md`, not a public issue containing sensitive details.
