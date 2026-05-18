# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

UniqueBible is a cross-platform, offline Bible application with integrated high-quality resources and unique features. It supports multiple platforms including Windows, macOS, Linux, Chrome OS, Android, and iOS.

## Development Setup

Python 3.8+ required.

```bash
# Install in development mode (registers console scripts)
pip install -e .

# Run tests
pytest
# Run a single test
pytest tests/test_uba.py::test_uba
```

Dependencies are listed in `uniquebible/requirements.txt`. Main dependencies include PySide6 (Qt), prompt_toolkit, openai, groq, mistralai, apsw, and gdown.

## Running the Application

The package `uniquebible` contains the main entry point `uba.py`. After `pip install -e .`, several console scripts are available:

| Command | Mode |
|---------|------|
| `ubgui` | GUI mode (single process) |
| `ubterm` | Terminal mode |
| `ubhttp` | HTTP server |
| `ubapi` | API client (remote) |
| `ubal` | API client (localhost) |
| `ubssh` | SSH server |
| `ubtelnet` | Telnet server |

You can also run directly without installing:
```bash
python uniquebible/uba.py gui
python uniquebible/uba.py terminal
python uniquebible/uba.py http-server
python uniquebible/uba.py api-server
```

Shell helper scripts for server management are in `uniquebible/http-server.sh`, `uniquebible/api-server.sh`, `uniquebible/kill-http-server.sh`, and `uniquebible/kill-api-server.sh`.

## High-Level Architecture

### Startup Flow

`uniquebible/uba.py` determines the run mode from `sys.argv`, then either exec-imports `uniquebible.main` directly (for CLI modes) or spawns it in a subprocess (for GUI mode on some platforms). `uniquebible/main.py` performs the actual startup sequence:

1. Import `uniquebible.config` and call `ConfigUtil.setup()` to initialize the global configuration.
2. Import `uniquebible.util.checkup` to validate dependencies and auto-download initial databases if missing.
3. Branch to either `uniquebible.startup.guiQt` (GUI modes) or `uniquebible.startup.nonGui` (terminal, HTTP, API, SSH, telnet, macro execution).

### Configuration System

Configuration is stored as module-level attributes in `uniquebible/config.py`. It is not a dictionary or class instance; code accesses settings via `import config` and reads or mutates `config.foo` directly. `ConfigUtil.setup()` populates defaults at runtime, and `ConfigUtil.save()` persists changes back to the file. Be careful when modifying config values—changes are global and often immediate.

### Command Dispatch

The application is built around a text-command architecture. `uniquebible/util/TextCommandParser.py` is the central dispatcher that parses user input and routes it to the appropriate handler. This parser is used across GUI, terminal, and HTTP modes. Commands are typically strings like `BIBLE:::KJV:::John 3:16` or `STUDY:::Wesley:::John 3:16`.

### GUI Architecture

GUI mode uses Qt via PySide6 (with qtpy as a fallback). The main window class in `uniquebible/gui/MainWindow.py` is the base, but the actual layout/menu implementation is selected at runtime via `config.menuLayout`. Built-in layout variants live in:
- `AlephMainWindow.py`
- `ClassicMainWindow.py`
- `FocusMainWindow.py`
- `MaterialMainWindow.py`

The selected layout class dynamically creates menus and toolbars on the base `MainWindow` instance. GUI components heavily depend on the global `config` module for state.

### Plugin System

Plugins are Python files loaded dynamically from directories under `uniquebible/plugins/`. There are nine plugin types:
- **config** — runtime setting overrides (e.g., colors)
- **context** — right-click actions in Bible/Study windows
- **event** — hooks for system events
- **language** — custom Bible abbreviation support
- **layout** — custom menu layouts
- **menu** — top-level menu entries
- **startup** — executed on application start
- **shutdown** — executed on exit
- **chatGPT** — AI/chat integrations

Startup plugins are run from `uniquebible/startup/share.py` via `runStartupPlugins()`.

### Database Layer

The application uses SQLite via `apsw` (an alternative SQLite wrapper), not the standard library `sqlite3`. Key database modules in `uniquebible/db/` include:
- `BiblesSqlite.py` — primary Bible text storage and retrieval
- `ToolsSqlite.py` — commentaries, dictionaries, encyclopedias, etc.
- `JEPDSqlite.py` — JEPD (documentary hypothesis) data
- `NoteSqlite.py` — user notes and highlights
- `BibleVectorDatabase.py` — semantic search vectors

### Terminal and Server Modes

- **Terminal mode** uses `prompt_toolkit` for interactive CLI input. History is stored in `terminal_history/commands`. The handler is set up in `uniquebible/startup/nonGui.py`.
- **HTTP server** uses `uniquebible/util/RemoteHttpHandler.py`.
- **API server** uses `uniquebible/util/RemoteApiHandler.py`.
- **SSH server** uses `asyncssh`.

These modes intentionally avoid importing Qt (`config.noQt = True`), so they can run headless.

## Testing

Test files are in `tests/`. The current test suite is minimal (a single stub test in `tests/test_uba.py`). `pytest.ini` points `testpaths` to `tests/`.

## Resources

- Wiki: https://github.com/eliranwong/UniqueBible/wiki
- GitHub: https://github.com/eliranwong/UniqueBible
- Website: https://bible.gospelchurch.uk
