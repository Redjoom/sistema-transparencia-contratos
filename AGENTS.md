# AGENTS.md

## WAT Framework

This project follows the **WAT** (Workflows, Agents, Tools) architecture defined in `../CLAUDE.md` (parent dir). Read that first.

- **Workflows** → `workflows/` — Markdown SOPs
- **Tools** → `tools/` — deterministic Python scripts
- **`.env`** holds all secrets — never commit it
- **`.tmp/`** for disposable intermediates; deliverables go to cloud services
- **`credentials.json`, `token.json`** for Google OAuth (gitignored)

## Project

**Sistema Institucional de Transparencia** — offline desktop app for auditing and auto-testing contracts under Mexican LGTAIP law.

**Tech stack:** Python, PyQt5, Ollama (local model: phi3), PyMuPDF, regex

## Setup

```bash
pip install PyQt5 PyMuPDF
```

## Current state

The app has one functional module: **Versión Pública PDF** — load a PDF, detect PII (RFC, CURP, email, phone, etc.) via regex, redact selected items using PyMuPDF's real redaction API, and save the public version.

No AI features implemented yet. All detection is regex-only.

## Source layout

```
main.py              # Entry point — python main.py (shows login first)
core/
├── pii_detector.py  # Regex patterns for Mexican PII (RFC, CURP, INE, etc.)
├── pdf_loader.py    # PyMuPDF wrapper — open, extract text + blocks
├── redactor.py      # Apply redaction annotations via PyMuPDF API
├── pdf_generator.py # Save redacted PDF (garbage-collected, deflated)
├── report_generator.py # Generate "oficio" PDF — foja, elemento, usuario, resumen
├── auth.py          # User validation via data/users.json (SHA-256)
└── activity_log.py  # Append-only JSONL log in data/actividad.jsonl
ui/
├── styles.py        # Windows classic institutional QSS theme
├── login_dialog.py  # Modal login with username + password
└── main_window.py   # QMainWindow — split view, PII list, preview, report
data/
├── users.json       # Auto-created with default admin/admin
└── actividad.jsonl  # Every action logged with user + timestamp
```

## Running

```bash
python main.py
```

Default credentials: `admin` / `admin`

## Build executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "SIT" --add-data "core;core" --add-data "ui;ui" --hidden-import "fitz" --hidden-import "PyQt5.sip" main.py
```

Output: `dist/SIT.exe`

## Default user

Created automatically on first run in `data/users.json`:
- **admin** / **admin** — nombre: Administrador, departamento: Sistemas

Use `core.auth.add_user(username, password, nombre, departamento)` to add more.

## Activity logging

Every action (open PDF, detect, redact, save, generate report, login/logout) is logged to `data/actividad.jsonl` with user, timestamp, and detail. Append-only — never delete entries.

## Key constraints

- Ollama is **not required** — all detection is regex-based
- PyMuPDF's `add_redact_annot` + `apply_redactions` performs **real data removal** from the PDF stream (not visual overlay)
- `data/` directory is gitignored — user credentials and activity logs stay local
- No build/test/lint toolchain configured yet
