# Media File Sorter and Searcher

This project helps you organize and find your photos and videos using powerful command-line tools or an easy-to-use graphical interface.

**⚡ New to this project?** Check out [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) for a quick start guide and common commands.

## Overview

The Media Organizer includes three main tools:

1. **Media Sorter** (`src/media_sorter.py`) - Automatically organizes your media files into a clean YYYY/MM folder structure
2. **Media Searcher** (`src/media_searcher.py`) - Quickly find files by date, keywords, or ratings
3. **GUI Application** (`run_gui.py`) - User-friendly interface for both tools

## Quick Start

### Using the GUI (Recommended)

Simply run:
```bash
python3 run_gui.py
```

The GUI provides an easy-to-use interface for both sorting and searching your media files.

## Media Sorter (`media_sorter.py`)

This Python script helps you organize your photos and videos into a structured folder hierarchy based on their creation date. It uses the powerful command-line tool `exiftool` to read metadata from the files.

The script will create folders in the format `YYYY/MM` (e.g., `2023/10`) in your specified destination directory.

### Features

*   **Sorts by Creation Date**: Organizes files based on their EXIF creation date.
*   **YYYY/MM Folder Structure**: Creates a clean and intuitive folder structure.
*   **Move or Copy**: Choose to either move the files to the new directory structure or create copies.
*   **Dry Run Mode**: Simulate the sorting process to see what changes will be made without actually touching any files. This is highly recommended for the first run!
*   **Filename Conflict Resolution**: Automatically renames files if a file with the same name already exists in the destination directory (e.g., `image_1.jpg`).
*   **Fallback Options**: If EXIF data is not available, optionally use the file's creation or modification time as a fallback.
*   **Fast Performance**: Optimized to process thousands of files quickly.

### Prerequisites

You must have `exiftool` installed on your system and accessible from your command line.

*   **Website & Installation**: https://exiftool.org/

To check if it's installed correctly, open a terminal or command prompt and run:

```bash
exiftool -ver
```

If it prints a version number, you're good to go.

### How to Use

1.  **Save the Script**: Save the `media_sorter.py` script to your computer.
2.  **Open Terminal**: Open a terminal or command prompt and navigate to the directory where you saved the script.
3.  **Run the Script**: Execute the script with the following command structure:

```bash
python3 src/media_sorter.py <source_directory> <destination_directory> [options]
```

#### Arguments

*   `source_directory`: The path to the folder containing the media files you want to sort.
*   `destination_directory`: The path to the folder where the sorted files will be placed.

#### Options

*   `--copy`: Copy files instead of moving them. This is safer if you want to keep the original files untouched.
*   `--dry-run`: Simulate the sorting process. The script will show what it would do, but no files will be moved or copied. **Recommended for first run!**
*   `--fallback-to-file-time {created,modified}`: Use file creation or modification time when EXIF data is not available. Options are `created` or `modified`.

### Examples

#### Dry Run (Recommended First Step)

This will show you which files will be moved where, without making any changes.

```bash
python3 src/media_sorter.py /path/to/your/photos /path/to/sorted/photos --dry-run
```

#### Move Files

This will move all media from the source folder to the sorted destination folders.

```bash
python3 src/media_sorter.py /path/to/your/photos /path/to/sorted/photos
```

#### Copy Files

This will copy the files, leaving your original folder intact.

```bash
python3 src/media_sorter.py /path/to/your/photos /path/to/sorted/photos --copy
```

#### Use Fallback for Files Without EXIF Data

This will use the file modification time when EXIF data is not available.

```bash
python3 src/media_sorter.py /path/to/your/photos /path/to/sorted/photos --fallback-to-file-time modified
```

## Media Searcher (`media_searcher.py`)

This script allows you to search for media files within the sorted directory structure created by the `media_sorter.py` script. Search by year, month, keywords, or ratings.

### Features

*   **Year & Month Filtering**: Search by specific years, months, or ranges
*   **Keyword Search**: Find files by keywords in path or metadata (case-insensitive)
*   **Rating Filters**: Search by star ratings or filter for accepted/rejected files
*   **Smart Directory Opening**: Automatically opens folders containing matched files
*   **Fast Performance**: Optimized to skip irrelevant directories and search efficiently

### How to Use

```bash
python3 src/media_searcher.py <search_directory> [options]
```

#### Arguments

*   `search_directory`: The path to the folder where your sorted media is located.

#### Options

*   `--year <year>` or `-y <year>`: Specify a single year or a range of years (e.g., `2022`, `2020-2023`).
*   `--month <month>` or `-m <month>`: Specify a single month or a range of months (e.g., `1`, `3-6`).
*   `--keyword <keyword1> [<keyword2> ...]` or `-k <keyword1> [<keyword2> ...]`: Specify one or more keywords to search for in the directory path or in the file's metadata keywords. The search is case-insensitive.
*   `--keyword-match <any|all>`: Use with multiple keywords. `any` (default) will find files that match any of the keywords. `all` will find files that match all of the keywords in the path or metadata.
*   `--rating <rating>` or `-r <rating>`: Specify a single rating or a range of ratings (e.g., `4`, `3-5`). Values must be between -1 and 5. Mutually exclusive with `--rejected` and `--picked`.
*   `--rejected` or `-R`: Search for rejected files (rating of -1). Mutually exclusive with `--rating` and `--picked`.
*   `--picked` or `-P`: Search for picked files (rating of 0-5). Mutually exclusive with `--rating` and `--rejected`.
*   `--open-dirs`: If specified, the script will open the directories containing the matched files in the default file explorer.

### Examples

#### Search by Year

```bash
python3 src/media_searcher.py /path/to/sorted/photos --year 2023
```

#### Search by Year Range

```bash
python3 src/media_searcher.py /path/to/sorted/photos --year 2021-2023
```

#### Search by Month

```bash
python3 src/media_searcher.py /path/to/sorted/photos --year 2023 --month 3
```

#### Search by Month Range

```bash
python3 src/media_searcher.py /path/to/sorted/photos --year 2023 --month 6-8
```

#### Search by Keyword

```bash
python3 src/media_searcher.py /path/to/sorted/photos --keyword vacation
```

#### Search by Multiple Keywords (any match)

Find files that contain ANY of the keywords:

```bash
python3 src/media_searcher.py /path/to/sorted/photos --keyword birthday vacation
```

#### Search by Multiple Keywords (all match)

Find files that contain ALL of the keywords:

```bash
python3 src/media_searcher.py /path/to/sorted/photos --keyword vacation skiing --keyword-match all
```

#### Search by Rating

```bash
python3 src/media_searcher.py /path/to/sorted/photos --rating 4
```

#### Search by Rating Range

```bash
python3 src/media_searcher.py /path/to/sorted/photos --rating 3-5
```

#### Search for Rejected Files

Find all files with a rating of -1:

```bash
python3 src/media_searcher.py /path/to/sorted/photos --rejected
```

#### Search for Picked Files

Find all files with ratings 0-5 (accepted files):

```bash
python3 src/media_searcher.py /path/to/sorted/photos --picked
```

#### Search and Open Directories

This will find all files from 2023 and automatically open the directories containing the matched files:

```bash
python3 src/media_searcher.py /path/to/sorted/photos --year 2023 --open-dirs
```

#### Combine Multiple Filters

Find vacation photos from summer 2023 with high ratings:

```bash
python3 src/media_searcher.py /path/to/sorted/photos --year 2023 --month 6-8 --keyword vacation --rating 4-5 --open-dirs
```

## Media Organizer GUI (`media_organizer_gui.py`)

For users who prefer a graphical interface, this project includes a user-friendly GUI that provides access to both the Media Sorter and Media Searcher functionality without needing to use the command line.

### Features

*   **Tabbed Interface**: Separate tabs for Media Sorter and Media Searcher operations
*   **Visual Controls**: Browse buttons, checkboxes, and input fields for all options
*   **Real-time Output**: Live progress updates and results displayed in expandable output areas
*   **Cross-platform**: Works on Windows, macOS, and Linux
*   **Threaded Execution**: Operations run in background threads, keeping the interface responsive
*   **ExifTool Check**: Automatically checks if ExifTool is installed on startup

### Prerequisites

The GUI has the same prerequisites as the command-line scripts:
*   Python 3.x
*   `exiftool` installed and accessible from the command line

### How to Use

#### Launch the GUI

```bash
python3 run_gui.py
```

#### Media Sorter Tab

The Media Sorter tab provides a graphical interface for organizing your media files:

1. **Select Directories**: Use the "Browse" buttons to select your source and destination directories
2. **Choose Options**:
   - **Copy files**: Check to copy files instead of moving them
   - **Dry run**: Check to simulate the process without making changes (recommended first!)
   - **Fallback to file time**: Choose whether to use file creation or modification time when EXIF data is unavailable
3. **Run**: Click "Run Media Sorter" to start
4. **View Output**: Expand the output section to see real-time progress and results

#### Media Searcher Tab

The Media Searcher tab provides a graphical interface for finding media files:

1. **Select Directory**: Use the "Browse" button to select the directory to search in
2. **Apply Filters** (all optional):
   - **Year**: Enter a single year (e.g., `2022`) or year range (e.g., `2020-2023`)
   - **Month**: Enter a single month (e.g., `1`) or month range (e.g., `3-6`)
   - **Keywords**: Enter space-separated keywords to search for
   - **Keyword Match**: Choose "Any" to find files matching any keyword, or "All" to require all keywords
   - **Rating Filters**: Choose from:
     - No rating filter
     - Specific rating/range (e.g., `4` or `3-5`)
     - Rejected files (rating of -1)
     - Picked files (rating of 0-5)
3. **Choose Options**:
   - **Open directories**: Check to automatically open directories containing matched files
4. **Search**: Click "Run Media Searcher" to start
5. **View Results**: Expand the output section to see matched files

### Advantages of the GUI

*   **Ease of Use**: No need to remember command-line syntax
*   **Visual Feedback**: See exactly what options are selected
*   **Error Prevention**: Form validation helps prevent common mistakes
*   **Progress Monitoring**: Watch operations in real-time with live output
*   **File Browser Integration**: Built-in directory browser eliminates typing file paths

## Troubleshooting

### "ExifTool not installed" or "exiftool is not installed or not in your PATH"

ExifTool is required for both scripts to work. Install it from https://exiftool.org/ and make sure it's accessible from the command line. Test by running `exiftool -ver` in your terminal.

### "Could not determine creation date"

This means ExifTool could not read the creation date from the file. This can happen if:
- The file is not a media file (photos/videos)
- The file does not have EXIF metadata

**Solution**: Use the `--fallback-to-file-time` option to use the file's creation or modification time instead.

### No files found when searching

Make sure:
- You're searching in the correct directory
- Your filters aren't too restrictive
- The directory structure follows the YYYY/MM format created by the sorter
- Hidden files (starting with `.`) are excluded from searches

### GUI doesn't start

Make sure you have Python 3 installed with tkinter support. On some Linux systems, you may need to install it separately:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

## Performance Tips

- **Media Sorter**: The script is optimized to process large libraries efficiently. Expect to process 1000+ files in just a few seconds.
- **Media Searcher**: Use year and month filters to narrow down searches faster. The script automatically skips irrelevant directories.
- **First Run**: Always use `--dry-run` first to preview changes before actually moving files.

## Project Structure

See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for details about how the project is organized.

## Additional Information

For more details about the scripts or to report issues, see the project repository.