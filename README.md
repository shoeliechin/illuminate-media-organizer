# Media File Sorter and Searcher

This project contains two Python scripts to help you organize and find your media files.

## Media Sorter (`media_sorter.py`)

This Python script helps you organize your photos and videos into a structured folder hierarchy based on their creation date. It uses the powerful command-line tool `exiftool` to read metadata from the files.

The script will create folders in the format `YYYY/MM` (e.g., `2023/10`) in your specified destination directory.

### Features

*   **Sorts by Creation Date**: Organizes files based on their EXIF creation date.
*   **YYYY/MM Folder Structure**: Creates a clean and intuitive folder structure.
*   **Move or Copy**: Choose to either move the files to the new directory structure or create copies.
*   **Dry Run Mode**: Simulate the sorting process to see what changes will be made without actually touching any files. This is highly recommended for the first run!
*   **Filename Conflict Resolution**: Automatically renames files if a file with the same name already exists in the destination directory (e.g., `image_1.jpg`).
*   **Fallback to File Modification Time**: If EXIF data is not available, the script will use the file's last modification time as a fallback.

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
python media_sorter.py <source_directory> <destination_directory> [options]
```

#### Arguments

*   `source_directory`: The path to the folder containing the media files you want to sort.
*   `destination_directory`: The path to the folder where the sorted files will be placed.

#### Options

*   `--copy`: Use this flag to copy the files instead of moving them. This is safer if you want to keep the original files untouched.
*   `--dry-run`: Use this flag to simulate the sorting process. The script will print what it would do, but no files will be moved or copied.

### Examples

#### Dry Run (Recommended First Step)

This will show you which files will be moved where, without making any changes.

```bash
python media_sorter.py /path/to/your/photos /path/to/sorted/photos --dry-run
```

#### Move Files

This will move all media from the source folder to the sorted destination folders.

```bash
python media_sorter.py /path/to/your/photos /path/to/sorted/photos
```

#### Copy Files

This will copy the files, leaving your original folder intact.

```bash
python media_sorter.py /path/to/your/photos /path/to/sorted/photos --copy
```

## Media Searcher (`media_searcher.py`)

This script allows you to search for media files within the sorted directory structure created by the `media_sorter.py` script.

### How to Use

```bash
python media_searcher.py <search_directory> [options]
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
python media_searcher.py /path/to/sorted/photos --year 2023
```

#### Search by Year Range

```bash
python media_searcher.py /path/to/sorted/photos --year 2021-2023
```

#### Search by Month

```bash
python media_searcher.py /path/to/sorted/photos --year 2023 --month 3
```

#### Search by Keyword

```bash
python media_searcher.py /path/to/sorted/photos --keyword vacation
```

#### Search by Multiple Keywords (any match)

```bash
python media_searcher.py /path/to/sorted/photos --keyword birthday vacation
```

#### Search by Multiple Keywords (all match)

```bash
python media_searcher.py /path/to/sorted/photos --keyword vacation skiing --keyword-match all
```

#### Search by Rating

```bash
python media_searcher.py /path/to/sorted/photos --rating 4
```

#### Search for Rejected Files

```bash
python media_searcher.py /path/to/sorted/photos --rejected
```

#### Search for Picked Files

```bash
python media_searcher.py /path/to/sorted/photos --picked
```

#### Search and Open Directories

This will find all files from 2023 and open the parent directories of the matched files.

```bash
python media_searcher.py /path/to/sorted/photos --year 2023 --open-dirs
```

## Media Organizer GUI (`media_organizer_gui.py`)

For users who prefer a graphical interface, this project includes a user-friendly GUI that provides access to both the Media Sorter and Media Searcher functionality without needing to use the command line.

### Features

*   **Tabbed Interface**: Separate tabs for Media Sorter and Media Searcher operations
*   **Visual Controls**: Browse buttons, checkboxes, and input fields for all options
*   **Real-time Output**: Live progress updates and results displayed in scrollable text areas
*   **Cross-platform**: Built with tkinter (included with Python) and works on Windows, macOS, and Linux
*   **Threaded Execution**: Operations run in background threads, keeping the interface responsive

### Prerequisites

The GUI has the same prerequisites as the command-line scripts:
*   Python 3.x
*   `exiftool` installed and accessible from the command line

### How to Use

#### Launch the GUI

```bash
python3 media_organizer_gui.py
```

Or use the launcher script:

```bash
python3 run_gui.py
```

#### Media Sorter Tab

The Media Sorter tab provides a graphical interface for organizing your media files:

*   **Directories**: Use the "Browse" buttons to select your source and destination directories
*   **Options**:
    *   **Copy files**: Check to copy files instead of moving them
    *   **Dry run**: Check to simulate the process without making changes
    *   **Fallback to file time**: Choose whether to use file creation or modification time when EXIF data is unavailable
*   **Output**: Real-time progress and results are displayed in the output area

#### Media Searcher Tab

The Media Searcher tab provides a graphical interface for finding media files:

*   **Search Directory**: Use the "Browse" button to select the directory to search in
*   **Filters**:
    *   **Year**: Enter a single year (e.g., `2022`) or year range (e.g., `2020-2023`)
    *   **Month**: Enter a single month (e.g., `1`) or month range (e.g., `3-6`)
    *   **Keywords**: Enter space-separated keywords to search for
    *   **Keyword Match**: Choose "Any" to find files matching any keyword, or "All" to require all keywords
    *   **Rating Filters**: Choose from no filter, specific rating/range, rejected files (-1), or picked files (0-5)
*   **Options**:
    *   **Open directories**: Check to automatically open directories containing matched files
*   **Results**: Search results are displayed in real-time in the results area

### Advantages of the GUI

*   **Ease of Use**: No need to remember command-line syntax
*   **Visual Feedback**: See exactly what options are selected
*   **Error Prevention**: Form validation helps prevent common mistakes
*   **Progress Monitoring**: Watch operations in real-time with live output
*   **File Browser Integration**: Built-in directory browser eliminates typing file paths

## Troubleshooting

### "Could not process metadata"

This error message means that `exiftool` could not read the creation date from the file. This can happen if the file is not a media file, or if it does not have any EXIF data. The script will automatically fall back to using the file's last modification time.