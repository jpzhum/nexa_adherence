# Nexa Adherence

Python data automation desktop application for ingesting and normalising operational records, persisting them in SQLite, analysing adherence, and producing controlled local exports.

> **Em português:** aplicação desktop para consolidar dados operacionais, aplicar filtros e regras, analisar indicadores e gerar relatórios locais.

## Project overview

Nexa Adherence turns recurring spreadsheet and CSV inputs into a consistent local analysis workflow. It combines operational records with equipment and supervisor reference data, builds a date-and-equipment base, evaluates expected records by shift, and presents the result through indicators, charts, and exportable reports.

The repository contains two implementations. `v2` is the current, recommended version; `v1` is retained as a legacy reference and fallback.

## Problem and solution

Operational data often arrives in separate files with inconsistent headers, repeated imports, and no single view of expected versus delivered records. Nexa Adherence provides a local workflow that:

1. loads equipment and supervisor reference files;
2. imports operational files from a selected folder;
3. normalises supported columns, dates, equipment identifiers, and shift labels;
4. stores v2 imports and reference data in SQLite, detecting previously imported files by SHA-256 hash;
5. consolidates a selected date range and applies configured exclusions and shift rules;
6. calculates delivery, missing-record, status, and adherence fields; and
7. displays indicators and charts or exports the consolidated results.

## Key features

- Desktop interface built with PyQt5.
- Recursive folder import for `.xlsx`, `.xls`, `.xlsm`, and `.csv` files.
- Header aliases and UTF-8/Latin-1 CSV handling for supported input schemas.
- SQLite persistence in v2 for imports, operational records, reference bases, rules, chart presets, and configuration.
- Duplicate-file detection and record upserts during v2 imports.
- Date-range consolidation with equipment/group exclusions and configurable shift rules.
- Summary indicators and Matplotlib dashboards.
- Multi-sheet Excel reports and a flat Excel export intended for downstream analysis.
- Formula-like text is neutralised before v2 Excel export to prevent imported values from being evaluated as formulas.
- Local HTML export; optional PDF generation is implemented through ReportLab.
- Optional Outlook desktop integration on Windows, plus manual package export when Outlook is unavailable.
- Local recipient-list management and rotating application logs.

## v1 and v2

| Area | v1 (legacy) | v2 (recommended) |
| --- | --- | --- |
| Role | Reference/fallback implementation | Current primary implementation |
| Desktop UI | PyQt5 multi-page interface | PyQt5 multi-page interface with background workers for import and consolidation |
| Data loading | File-oriented services and local configuration | Dedicated parsers and import services |
| Persistence | SQLite schema is present | Versioned SQLite schema and repository layer |
| Import tracking | Basic application flow | File hashes, import status, error log, and record upserts |
| Configuration | Local JSON-oriented services | Configuration, rules, and reference data stored in SQLite; optional environment overrides |
| Tests and lint | Excluded from Ruff and not directly covered by the current tests | Covered by the repository's parser, service, and pipeline tests; included in Ruff checks |
| Installation | `v1/requirements.txt` | Root `pyproject.toml` with optional GUI, Outlook, and development dependency groups |

See [v1/README.md](v1/README.md) and [v2/README.md](v2/README.md) for version-specific notes.

## Architecture

The v2 application is organised into distinct layers:

```text
PyQt5 UI
  -> service layer (import, consolidation, analysis, reports, e-mail)
     -> parsers and validation
     -> SQLite repositories
        -> local SQLite database
```

Long-running imports and consolidations run through Qt worker threads so the interface can report progress. Consolidated results are held in an in-process result store for the dashboard, indicators, reporting, and export pages.

## Repository structure

```text
.
|-- v2/                    # Recommended application
|   |-- db/                # SQLite connection, schema, and repositories
|   |-- parsers/           # Supported input readers and schema normalisation
|   |-- services/          # Import, analysis, consolidation, and export logic
|   |-- ui/                # PyQt5 window, pages, charts, and workers
|   `-- app.py             # v2 entry point
|-- v1/                    # Legacy implementation and documentation
|-- tests/                 # v2 parser, service, and pipeline tests
|-- .github/workflows/     # Continuous integration
`-- pyproject.toml         # Package metadata, dependencies, and tool configuration
```

## Technology stack

- Python 3.10+
- pandas, openpyxl, and xlrd for tabular data and Excel files
- PyQt5 and PyQtWebEngine for the optional desktop interface
- SQLite from the Python standard library
- Matplotlib for charts
- ReportLab for PDF generation
- pywin32 for optional Outlook integration on Windows
- pytest and Ruff for automated quality checks
- GitHub Actions for CI on Python 3.12

## Quick start

The commands below use PowerShell. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev,gui]"
python v2/app.py
```

For optional Outlook desktop integration on Windows:

```powershell
pip install -e ".[outlook]"
```

The core dependency set does not include the GUI packages. Install the `gui` extra before starting either desktop application.

## Configuration

The application reads these optional environment variables:

| Variable | Purpose | Default behaviour |
| --- | --- | --- |
| `NEXA_V2_DB_PATH` | Override the v2 SQLite database path | Uses `v2/data/nexa_v2.db` |
| `NEXA_DEFAULT_TO` | Comma-separated default primary recipients | Uses the safe application placeholder |
| `NEXA_DEFAULT_CC` | Comma-separated default CC recipients | Uses the safe application placeholder |

`.env.example` is a reference template only: the application does not automatically load `.env` files. Set variables in the shell or provide them through your execution environment, for example:

```powershell
$env:NEXA_V2_DB_PATH = ".\v2\data\nexa_v2.db"
$env:NEXA_DEFAULT_TO = "user@example.com"
python v2/app.py
```

Recipient lists can also be managed in the UI. Local recipient data is stored beside the v2 database and is ignored by Git. The files `v1/destinatarios.example.json` and `v2/destinatarios.example.json` contain safe example structures only.

## Running the application

Recommended v2 entry point, from the repository root:

```powershell
python v2/app.py
```

Legacy v1 entry point:

```powershell
cd v1
pip install -r requirements.txt
python app.py
```

The normal v2 workflow is **reference bases -> operational import -> consolidation -> indicators/dashboard -> report or export**. Input files must contain a supported set of columns; the parsers raise explicit validation errors when required data is missing.

## Tests and quality

Run the same checks expected for repository contributions:

```powershell
ruff check .
ruff format --check .
python -m pip check
pytest -q
```

The tests exercise v2 input parsing, exclusion and shift logic, consolidation scenarios, export schema compatibility and formula neutralisation, indicator rendering, e-mail template hygiene, and recipient validation. They do not exercise the graphical interface, Outlook automation, or the legacy v1 implementation.

GitHub Actions runs dependency checks, Ruff lint and format checks, and pytest on Python 3.12 for every push and pull request.

## Limitations

- The application is a local desktop tool, not a hosted or multi-user service.
- Input validation supports known column aliases but does not infer arbitrary schemas.
- Consolidation requires populated equipment and supervisor reference bases.
- Application state and recipient configuration are local to the selected SQLite data directory.
- Outlook sending requires Windows, Outlook desktop, and the optional `pywin32` dependency. Exporting a package remains available without Outlook.
- Automated tests focus on v2 business services and parsers; UI, Outlook, and v1 flows require manual verification.
- Formula neutralisation is implemented and tested for v2 exports; use legacy v1 exports only with trusted input files.

## Data privacy

Nexa Adherence is designed for local processing. Imported content, SQLite databases, generated reports, recipient lists, and logs may contain operational or personal data and must not be committed to a public repository.

The `.gitignore` excludes local environment files, common spreadsheet inputs, data directories, databases, logs, recipient lists, and generated build output. Example configuration uses reserved `example.com` addresses. Before publishing a fork, review the full working tree and Git history independently; ignore rules do not remove previously committed content.

For vulnerability reporting guidance, see [SECURITY.md](SECURITY.md).

## Project status

Version 2.0.0 is the primary implementation in this repository. It is suitable as a portfolio and development project, but no production SLA, performance benchmark, deployment guarantee, or business outcome is claimed. The v1 tree remains available for legacy reference.

No screenshots are currently tracked. A future documentation update may add sanitised images under `docs/images/` after verifying that they contain no operational data, personal information, local paths, or recipient details.

## Contributing

Contributions are welcome through focused pull requests. Install the development dependencies, run all quality checks, and never include real input files, databases, recipient lists, logs, or secrets. See [CONTRIBUTING.md](CONTRIBUTING.md) for the repository workflow.

## License

This project is available under the [MIT License](LICENSE).
