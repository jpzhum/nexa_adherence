Deployment Guide (v2)
=====================

Purpose
-------
This guide explains how to run, package, and deploy the v2 app inside the company
environment. It includes dependencies, setup steps, and PyInstaller notes.


1) Requirements
---------------
- Python 3.10+ (Windows recommended for Outlook integration)
- pip (comes with Python)

Optional (feature-specific):
- PyQtWebEngine (needed for Indicators page)
- pywin32 (needed for Outlook email send)

Core Python packages used by v2:
- PyQt5
- pandas
- openpyxl
- matplotlib

Optional:
- PyQtWebEngine
- pywin32


2) Create a virtual environment (recommended)
---------------------------------------------
From the repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```


3) Install dependencies
-----------------------
Minimal install (core features):

```powershell
pip install PyQt5 pandas openpyxl matplotlib
```

Enable Indicators (HTML/WebEngine):

```powershell
pip install PyQtWebEngine
```

Enable Outlook email send:

```powershell
pip install pywin32
```


4) Run locally (dev mode)
-------------------------
From the repo root:

```powershell
python -m v2.app
```


5) Data storage (SQLite)
------------------------
The SQLite database is created automatically in:

```
v2/data/nexa_v2.db
```

Override location if needed (environment variable):

```
NEXA_V2_DB_PATH=C:\path\to\custom.db
```


6) User-configured settings (in app)
------------------------------------
- Configurations are stored in SQLite table `configs`.
- First run can import legacy `config.json` (v1) if it exists in the repo root.
- Exclusions in Settings affect consolidation and dashboard results.


7) Email behavior
-----------------
- If Outlook is installed, the app sends via Outlook.
- If Outlook is not available, use "Exportar pacote" in the Email page.
  It generates:
  - email_relatorio.html
  - PNG charts (attachments)
  - optional PDF (disabled by default in v2)


8) Packaging with PyInstaller
-----------------------------
Recommended single-file build (Windows):

```powershell
pyinstaller --noconfirm --onefile --windowed ^
  --name "NexaAderencia" ^
  --add-data "v2\\assets\\style.qss;v2\\assets" ^
  v2\\app.py
```

If you use Indicators (QtWebEngine), add:

```
--hidden-import PyQt5.QtWebEngineWidgets
```

If you use Outlook email:

```
--hidden-import win32com.client
```

If you use a dashboard layout JSON (optional):

```
--add-data "v2\\resources\\dashboard_layout.json;v2\\resources"
```

Output will be in:

```
dist\\NexaAderencia.exe
```


9) First run checklist (company PC)
-----------------------------------
- Start the EXE.
- Go to Bases and import BD EQP + BD Supervisor.
- Import apontamentos (Importacao).
- Consolidate.
- Validate Dashboard and Indicators.
- Configure Destinatarios if using email.


10) Troubleshooting
-------------------
Indicators page blank:
- Install PyQtWebEngine.

Email send fails:
- Outlook not installed or blocked -> use Exportar pacote.

Export errors:
- Excel file is open or locked; close and retry.


11) Maintenance notes
---------------------
- Keep v1 intact (read-only reference).
- v2 is the official source for data and output.
- Avoid changing KPI logic; follow v1 as spec.
