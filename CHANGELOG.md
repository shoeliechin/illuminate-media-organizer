# Changelog

All notable changes to the Illuminate Media Organizer project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-20

### Added
- **Media Sorter**: Command-line tool to organize photos and videos into YYYY/MM folder structure based on EXIF creation date
  - Move or copy files with `--copy` flag
  - Dry run mode with `--dry-run` to preview changes
  - Fallback to file creation/modification time when EXIF data unavailable
  - Automatic filename conflict resolution
  - Batch ExifTool processing for optimal performance (50-100x faster than sequential processing)
  - Interactive confirmation prompt for move operations with `--yes` flag to skip
  - Auto-open destination directory with `--open-dest` flag

- **Media Searcher**: Command-line tool to search organized media files
  - Search by year, month, or date ranges
  - Search by keywords in file paths or EXIF metadata
  - Search by star ratings (0-5) or rejected files (-1)
  - Multiple keyword matching modes (any/all)
  - Auto-open directories containing matched files with `--open-dirs`
  - Smart directory traversal that skips irrelevant folders

- **GUI Application**: User-friendly graphical interface
  - Tabbed interface for both Media Sorter and Media Searcher
  - Browse buttons for easy directory selection
  - Real-time output display with expandable sections
  - Cross-platform support (Windows, macOS, Linux)
  - Background threading keeps interface responsive
  - ExifTool availability check on startup

- **Documentation**:
  - Comprehensive README with usage examples and troubleshooting
  - Quick Reference guide for common commands
  - Project Structure documentation
  - GNU General Public License v3.0

- **Package Features**:
  - Modern Python packaging with pyproject.toml
  - Command-line entry points: `media-sorter`, `media-searcher`, `media-organizer-gui`
  - Zero external Python dependencies (uses only standard library)
  - Type hints for better code clarity
  - Comprehensive logging support

### Technical Details
- Requires Python 3.8 or higher
- Requires ExifTool (external dependency)
- Supports common photo formats: JPG, JPEG, PNG, HEIC, CR2, NEF, ARW, DNG
- Supports common video formats: MP4, MOV, AVI, MKV, M4V, 3GP

---

## [Unreleased]

### Planned
- Additional test coverage
- Performance benchmarks
- Additional video format support
- Configuration file support

---

**Note**: For detailed technical implementation changes and optimizations, see the developer documentation in `docs/OPTIMIZATION_SUMMARY.md` and `docs/MEDIUM_PRIORITY_OPTIMIZATIONS.md`.
