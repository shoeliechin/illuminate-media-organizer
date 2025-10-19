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
*   `--keyword <keyword1> [<keyword2> ...]` or `-k <keyword1> [<keyword2> ...]`: Specify one or more keywords to search for in the directory path. The search is case-insensitive.
*   `--keyword-match <any|all>`: Use with multiple keywords. `any` (default) will find files that match any of the keywords. `all` will find files that match all of the keywords in the path.

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

## Troubleshooting

### "Could not process metadata"

This error message means that `exiftool` could not read the creation date from the file. This can happen if the file is not a media file, or if it does not have any EXIF data. The script will automatically fall back to using the file's last modification time.