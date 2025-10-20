# Project Structure

This document describes the organization of the Media Organizer project.

## Directory Layout

```
media_organizer_script_v1/
├── run_gui.py                 # Main launcher - start here!
├── README.md                  # Complete documentation
├── LICENSE                    # GPLv3 license text
├── .gitignore                 # Git ignore rules
├── pyproject.toml             # Modern Python packaging configuration
├── requirements.txt           # Python dependencies (uses stdlib only)
│
├── src/                       # All Python source code
│   ├── __init__.py            # Package initialization
│   ├── __version__.py         # Version and metadata
│   ├── media_utils.py         # Shared utilities
│   ├── media_sorter.py        # Sorting script
│   ├── media_searcher.py      # Searching script
│   └── media_organizer_gui.py # GUI application
│
└── docs/                      # Documentation
    ├── PROJECT_STRUCTURE.md   # This file (project organization)
    ├── QUICK_REFERENCE.md     # Quick start guide
    └── OPTIMIZATION_SUMMARY.md # Technical optimization details
```

## Quick Start

For most users, simply run:
```bash
python3 run_gui.py
```

This launches the graphical interface which provides access to all functionality.

## File Descriptions

### Root Directory

- **`run_gui.py`** - Simple launcher script that starts the GUI application. This is the recommended entry point for most users.
- **`README.md`** - Complete project documentation with usage examples and troubleshooting.
- **`LICENSE`** - GNU General Public License v3.0 full text.
- **`.gitignore`** - Git ignore patterns for Python projects (excludes __pycache__, build artifacts, etc.).
- **`pyproject.toml`** - Modern Python packaging configuration (PEP 517/518 compliant).
- **`requirements.txt`** - Python dependencies list (this project uses only standard library).

### src/ Directory

Contains all Python source code:

- **`__init__.py`** - Makes src a proper Python package, exports version info.

- **`__version__.py`** - Version and metadata constants:
  - `__version__` - Current version (1.0.0)
  - `__author__` - Project author
  - `__license__` - License type (GPLv3)
  - `__description__` - Package description

- **`media_utils.py`** - Shared utility functions used by all scripts:
  - ExifTool detection
  - Date parsing
  - Directory operations
  - Batch metadata processing

- **`media_sorter.py`** - Command-line tool for organizing media files:
  - Sorts files into YYYY/MM folder structure
  - Can be run independently: `python3 src/media_sorter.py SOURCE DEST`
  - Main entry point: `main()` function

- **`media_searcher.py`** - Command-line tool for finding media files:
  - Search by year, month, keywords, or ratings
  - Can be run independently: `python3 src/media_searcher.py DIRECTORY [options]`
  - Main entry point: `main()` function

- **`media_organizer_gui.py`** - GUI application module:
  - Provides graphical interface for both sorter and searcher
  - Launched via `run_gui.py`
  - Main entry point: `main()` function

### docs/ Directory

All documentation files:

- **`PROJECT_STRUCTURE.md`** - This file; explains project organization
- **`QUICK_REFERENCE.md`** - Quick start guide with common commands and examples
- **`OPTIMIZATION_SUMMARY.md`** - Technical details about performance optimizations

## Running Scripts

### GUI (Recommended)
```bash
python3 run_gui.py
```

### Command Line

**Sorter:**
```bash
python3 src/media_sorter.py <source> <destination> [options]
```

**Searcher:**
```bash
python3 src/media_searcher.py <search_directory> [options]
```

## Design Decisions

### Why `src/` folder?

- **Clean separation**: Keeps source code separate from documentation and configuration
- **Professional structure**: Follows Python best practices
- **Easy navigation**: Users know where to find code vs. documentation
- **Scalability**: Easy to add new modules without cluttering the root

### Why `run_gui.py` in root?

- **Discoverability**: Users immediately see how to launch the application
- **Simplicity**: No need to navigate into folders for the most common use case
- **Clear entry point**: Makes it obvious how to start the program

### Why `docs/` folder?

- **Organization**: Keeps detailed documentation separate from the main README
- **Maintainability**: Easy to add more documentation without cluttering the root
- **Standard practice**: Many projects use a `docs/` folder

## Import Structure

The code uses flexible imports that work whether scripts are run directly or imported as modules:

```python
try:
    from media_utils import function
except ImportError:
    from src.media_utils import function
```

This allows:
- Running scripts directly from `src/`: `python3 src/media_sorter.py`
- Running the GUI launcher from root: `python3 run_gui.py`
- Future packaging as a proper Python module

## For Developers

If you're modifying the code:

1. **All Python code goes in `src/`** - Don't add Python files to the root
2. **Update both CLI scripts and GUI** - Keep them in sync
3. **Test both command-line and GUI** - Changes affect both interfaces
4. **Update documentation** - Keep README.md and QUICK_REFERENCE.md current
5. **Use shared utilities** - Add common functions to `media_utils.py`

## Adding New Features

To add a new feature:

1. Add core functionality to appropriate file in `src/`
2. Update command-line arguments if needed
3. Update GUI if feature should be exposed there
4. Add tests (if you create a test suite)
5. Update documentation in `README.md` and `docs/QUICK_REFERENCE.md`

## Installation and Packaging

### Using as a Python Package

To install the package in development mode:

```bash
pip install -e .
```

This installs the package with the following command-line tools:
- `media-sorter` - Runs the media sorter
- `media-searcher` - Runs the media searcher
- `media-organizer-gui` - Launches the GUI

### Building a Distribution

To build a wheel package:

```bash
pip install build
python -m build
```

This creates distribution files in the `dist/` directory.

### Installing from Source

```bash
git clone <repository-url>
cd media_organizer_script_v1
pip install .
```

## Version Control

The `.gitignore` file excludes:
- `__pycache__/` - Python bytecode
- `.venv/`, `venv/` - Virtual environments
- `dist/`, `build/`, `*.egg-info/` - Build artifacts
- `.pytest_cache/`, `.mypy_cache/` - Testing/linting cache
- Test media files
- Development artifacts

See `.gitignore` for complete list.

## License

This project is licensed under the GNU General Public License v3.0 or later.

Copyright (C) 2025  Shiue-Lang Chin

All source files include the GPLv3 license header. See LICENSE for full license text.
