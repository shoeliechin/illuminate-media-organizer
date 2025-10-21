# Illuminate Media Organizer

Organize and search your photos and videos using powerful command-line tools or an easy-to-use graphical interface.

**⚡ New here?** Check out the [Quick Reference Guide](docs/QUICK_REFERENCE.md) for common commands and examples.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Tools](#tools)
  - [Media Sorter](#media-sorter)
  - [Media Searcher](#media-searcher)
  - [GUI Application](#gui-application)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

Illuminate Media Organizer provides three tools to help you manage your media library:

| Tool | Description | Command |
|------|-------------|---------|
| **Media Sorter** | Organize files into YYYY/MM folders by date | `python3 src/media_sorter.py` or `media-sorter` |
| **Media Searcher** | Find files by date, keywords, or ratings | `python3 src/media_searcher.py` or `media-searcher` |
| **GUI Application** | User-friendly interface for both tools | `python3 run_gui.py` or `media-organizer-gui` |

---

## Installation

### Requirements

- **Python 3.8+** with tkinter support (for GUI)
- **ExifTool** - Download from [exiftool.org](https://exiftool.org/)

Verify ExifTool is installed:
```bash
exiftool -ver
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/shoeliechin/illuminate-media-organizer.git
cd illuminate-media-organizer

# Install as a package (optional - provides command-line tools)
pip install -e .
```

After installation, you can use:
- `media-sorter` instead of `python3 src/media_sorter.py`
- `media-searcher` instead of `python3 src/media_searcher.py`
- `media-organizer-gui` instead of `python3 run_gui.py`

---

## Quick Start

### Option 1: GUI (Recommended for Beginners)

```bash
python3 run_gui.py
```

The GUI provides an intuitive interface with visual controls for all features.

### Option 2: Command Line

**Organize your media:**
```bash
# Preview changes (recommended first!)
python3 src/media_sorter.py /path/to/photos /path/to/organized --dry-run

# Actually organize them
python3 src/media_sorter.py /path/to/photos /path/to/organized
```

**Search for files:**
```bash
# Find all photos from 2023 and open the folders
python3 src/media_searcher.py /path/to/organized --year 2023 --open-dirs
```

For more examples, see the [Quick Reference Guide](docs/QUICK_REFERENCE.md).

---

## Tools

### Media Sorter

Automatically organizes photos and videos into a clean folder structure based on creation date.

**What it does:**
- Reads EXIF metadata to get creation dates
- Creates YYYY/MM folder structure (e.g., `2023/10`)
- Moves or copies files to organized folders
- Handles filename conflicts automatically

**Key Features:**
- ✓ Dry run mode to preview changes
- ✓ Copy mode to preserve originals
- ✓ Fallback to file dates when EXIF unavailable
- ✓ Fast batch processing (1000+ files in seconds)

**Basic Usage:**
```bash
python3 src/media_sorter.py SOURCE DESTINATION [options]
```

**Common Options:**
- `--dry-run` - Preview without making changes
- `--copy` - Copy instead of move
- `--fallback-to-file-time modified` - Use file dates as fallback
- `--help` - Show all options

**Example Output Structure:**
```
Organized/
├── 2022/
│   ├── 01/
│   ├── 02/
│   └── ...
├── 2023/
│   ├── 01/
│   └── ...
```

See [Quick Reference](docs/QUICK_REFERENCE.md) for more examples.

---

### Media Searcher

Find media files in your organized library using flexible filters.

**Search by:**
- Year and month (single values or ranges)
- Keywords in filenames or EXIF metadata
- Star ratings (0-5) or rejected files (-1)
- Any combination of the above

**Key Features:**
- ✓ Fast searches with smart directory skipping
- ✓ Case-insensitive keyword matching
- ✓ Auto-open folders with results
- ✓ Multiple keyword modes (any/all)

**Basic Usage:**
```bash
python3 src/media_searcher.py DIRECTORY [options]
```

**Common Options:**
- `--year 2023` or `--year 2021-2023` - Filter by year
- `--month 6` or `--month 6-8` - Filter by month
- `--keyword vacation` - Search by keyword
- `--rating 4-5` - Filter by rating
- `--open-dirs` - Auto-open result folders
- `--help` - Show all options

**Example Searches:**
```bash
# Summer vacation photos from 2023
python3 src/media_searcher.py /organized --year 2023 --month 6-8 --keyword vacation

# High-rated photos
python3 src/media_searcher.py /organized --rating 4-5 --open-dirs

# All rejected files
python3 src/media_searcher.py /organized --rejected
```

See [Quick Reference](docs/QUICK_REFERENCE.md) for more examples.

---

### GUI Application

User-friendly graphical interface for users who prefer not to use the command line.

**Features:**
- Tabbed interface for Sorter and Searcher
- Browse buttons for easy directory selection
- Real-time progress display
- All CLI features available visually
- Cross-platform (Windows, macOS, Linux)

**Launch:**
```bash
python3 run_gui.py
```

**Tabs:**

**Media Sorter Tab:**
1. Select source and destination directories
2. Choose options (copy, dry-run, fallback)
3. Click "Run Media Sorter"
4. View live progress

**Media Searcher Tab:**
1. Select search directory
2. Set filters (year, month, keywords, rating)
3. Click "Run Media Searcher"
4. View results and optionally open folders

---

## Troubleshooting

### ExifTool Not Found

**Problem:** `exiftool is not installed or not in your PATH`

**Solution:** Install ExifTool from [exiftool.org](https://exiftool.org/) and verify:
```bash
exiftool -ver
```

---

### Could Not Determine Creation Date

**Problem:** `Could not determine creation date for file`

**Cause:** File has no EXIF metadata

**Solution:** Use fallback to file dates:
```bash
python3 src/media_sorter.py SOURCE DEST --fallback-to-file-time modified
```

---

### GUI Won't Start

**Problem:** GUI doesn't launch

**Solution:** Install tkinter for your system:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (usually pre-installed with Python)
# Windows (included with official Python installer)
```

---

### No Search Results

**Problem:** Searcher finds no files

**Check:**
- Correct directory path
- Directory structure is YYYY/MM format
- Filters aren't too restrictive
- Files aren't hidden (starting with `.`)

---

## Additional Resources

- **[Quick Reference Guide](docs/QUICK_REFERENCE.md)** - Common commands and examples
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - How the project is organized
- **[Changelog](CHANGELOG.md)** - Version history and changes

---

## License

This project is licensed under the **GNU General Public License v3.0** or later.

Copyright (C) 2025 Shiue-Lang Chin

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See the [LICENSE](LICENSE) file for full details.

---

## Version

**Current Version:** 1.0.0
**Author:** Shiue-Lang Chin
**Repository:** https://github.com/shoeliechin/illuminate-media-organizer

For bug reports and feature requests, please open an issue on GitHub.
