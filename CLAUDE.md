# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

UniqueBible is a cross-platform, offline Bible application with integrated high-quality resources and unique features. It supports multiple platforms including Windows, macOS, Linux, Chrome OS, Android, and iOS.

## Repository Structure

The codebase is organized as follows:
- Main application files: `uba.py`, `main.py`
- Configuration: `config.py` (central configuration file)
- GUI components: `gui/` directory with various Qt-based UI components
- Database utilities: `db/` directory with SQLite database handlers
- Plugins system: `plugins/` directory with various plugin types
- Utilities: `util/` directory with helper functions
- Resources: `htmlResources/` for web assets, `marvelData/` for Bible data
- Testing: `testing/` directory with test scripts

## Development Setup

1. Python 3.8+ required
2. Install dependencies: `pip install -r requirements.txt`
3. The application automatically sets up a virtual environment on first run
4. Main dependencies include PySide6 (Qt), prompt_toolkit, openai, groq, mistralai, and various other libraries

## Running the Application

### GUI Mode
```bash
python uba.py
# or
python uba.py gui
```

### Terminal Mode
```bash
python uba.py terminal
```

### Other Modes
- HTTP server: `python uba.py http-server`
- SSH server: `python uba.py ssh-server`
- Telnet server: `python uba.py telnet-server`
- API server: `python uba.py api-server`

## Configuration

The main configuration file is `config.py`, which contains:
- Enabled/disabled features and modules
- AI backend settings (OpenAI, Groq, Mistral, Google AI)
- Terminal mode settings
- GUI appearance settings
- Database paths and settings
- API keys and model configurations

## Architecture

The application follows a modular architecture:
- Entry point: `uba.py` -> `main.py`
- Configuration: Centralized in `config.py`
- GUI: Qt-based using PySide6
- Data: SQLite databases for Bibles, commentaries, dictionaries, etc.
- Plugins: Extensible plugin system in the `plugins/` directory
- AI Integration: Support for multiple AI backends (OpenAI, Groq, Mistral, Google AI)

## Key Components

1. **Main Application Flow**: `uba.py` -> `main.py` -> mode-specific startup files
2. **Configuration Management**: `config.py` and `util/ConfigUtil.py`
3. **Database Layer**: Various SQLite wrappers in `db/` directory
4. **GUI Components**: Qt widgets in `gui/` directory
5. **Plugin System**: Extensible plugins in `plugins/` directory
6. **Utilities**: Helper functions in `util/` directory

## Testing

Limited test files exist in the `testing/` directory. Testing appears to be primarily manual rather than automated.

## Resources

- Wiki: https://github.com/eliranwong/UniqueBible/wiki
- GitHub: https://github.com/eliranwong/UniqueBible
- Website: https://bible.gospelchurch.uk