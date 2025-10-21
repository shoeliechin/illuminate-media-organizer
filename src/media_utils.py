#!/usr/bin/env python3
"""
Shared utilities for the Illuminate Media Organizer project.
Contains common functions used across sorter, searcher, and GUI.

Copyright (C) 2025  Shiue-Lang Chin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import subprocess
import sys
import os
from datetime import datetime
from typing import Optional, Dict, List, Set, Iterator, Tuple
import json


# Supported media file extensions (case-insensitive)
MEDIA_EXTENSIONS: Set[str] = {
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
    '.heic', '.heif', '.raw', '.cr2', '.nef', '.arw', '.dng', '.orf',
    '.rw2', '.pef', '.srw', '.raf', '.crw', '.cr3',
    # Videos
    '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v',
    '.mpg', '.mpeg', '.3gp', '.mts', '.m2ts', '.vob', '.ogv', '.mxf'
}


def is_media_file(filename: str) -> bool:
    """
    Check if a file is a supported media file based on its extension.

    Args:
        filename: Name of the file (can be full path or just filename)

    Returns:
        True if the file has a supported media extension, False otherwise
    """
    _, ext = os.path.splitext(filename)
    return ext.lower() in MEDIA_EXTENSIONS


def is_exiftool_installed() -> bool:
    """Check if exiftool is installed and available in the system's PATH."""
    try:
        subprocess.run(['exiftool', '-ver'], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_pictures_directory() -> str:
    """Get the user's Pictures directory across different platforms."""
    try:
        if sys.platform == 'win32':
            # Windows: Use USERPROFILE\Pictures
            import winreg
            try:
                # Try to get the actual Pictures folder from registry
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
                pictures_path = winreg.QueryValueEx(key, "My Pictures")[0]
                winreg.CloseKey(key)
                if os.path.exists(pictures_path):
                    return pictures_path
            except (OSError, ImportError, KeyError):
                # OSError: Registry access failed
                # ImportError: winreg module not available
                # KeyError: Registry key not found
                pass
            # Fallback to standard location
            from pathlib import Path
            pictures = Path.home() / "Pictures"

        elif sys.platform == 'darwin':
            # macOS: ~/Pictures
            from pathlib import Path
            pictures = Path.home() / "Pictures"

        else:
            # Linux and other Unix-like systems
            # Try XDG user directories first
            try:
                result = subprocess.run(['xdg-user-dir', 'PICTURES'],
                                      capture_output=True, text=True, check=True)
                pictures_path = result.stdout.strip()
                if os.path.exists(pictures_path):
                    return pictures_path
            except (subprocess.CalledProcessError, FileNotFoundError, OSError):
                # FileNotFoundError: xdg-user-dir command not found
                # CalledProcessError: xdg-user-dir command failed
                # OSError: Other system errors
                pass
            # Fallback to standard location
            from pathlib import Path
            pictures = Path.home() / "Pictures"

        # Return the path if it exists, otherwise return home directory
        if pictures.exists():
            return str(pictures)
        else:
            from pathlib import Path
            return str(Path.home())

    except Exception:
        # Ultimate fallback to home directory
        from pathlib import Path
        return str(Path.home())


def scan_media_files(
    source_dir: str,
    chunk_size: int = 1000
) -> Iterator[List[str]]:
    """
    Generator that yields media files from a directory in chunks.
    Useful for processing very large directories without loading all paths into memory.

    Args:
        source_dir: Directory to scan for media files
        chunk_size: Number of files to yield per chunk (default: 1000)

    Yields:
        Lists of media file paths, each list containing up to chunk_size files
    """
    chunk: List[str] = []

    for root, _, files in os.walk(source_dir):
        for filename in files:
            # Skip hidden files
            if filename.startswith('.'):
                continue

            # Skip non-media files
            if not is_media_file(filename):
                continue

            source_path = os.path.join(root, filename)
            chunk.append(source_path)

            # Yield chunk when it reaches the specified size
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []

    # Yield remaining files
    if chunk:
        yield chunk


def get_creation_dates_batch(file_paths: List[str], verbose: bool = False) -> Dict[str, Optional[datetime]]:
    """
    Get creation dates for multiple media files using exiftool in batch mode.
    This is much faster than calling exiftool once per file.

    Args:
        file_paths: List of file paths to process
        verbose: If True, print progress information

    Returns:
        Dictionary mapping file_path -> datetime object (or None if date not found)
    """
    if not file_paths:
        return {}

    # Tags to check in order of preference
    date_tags = [
        'SubSecCreateDate', 'SubSecDateTimeOriginal', 'CreateDate',
        'DateTimeOriginal', 'MediaCreateDate', 'TrackCreateDate', 'ModifyDate'
    ]

    # Build the command to run exiftool in batch mode
    command = ['exiftool', '-json', '-d', '%Y-%m-%d %H:%M:%S']
    command.extend([f'-{tag}' for tag in date_tags])
    command.extend(file_paths)

    results = {}

    try:
        # Execute exiftool command for all files at once
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        metadata_list = json.loads(result.stdout)

        # Process each file's metadata
        for metadata in metadata_list:
            source_file = metadata.get('SourceFile')
            if not source_file:
                continue

            creation_date = None

            # Find the first available date from the preferred tags
            for tag in date_tags:
                if tag in metadata:
                    date_str = metadata[tag]
                    creation_date = parse_date_string(date_str)
                    if creation_date:
                        break  # Successfully parsed, use this date

            results[source_file] = creation_date

        return results

    except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError) as e:
        if verbose:
            print(f"Error processing batch metadata: {e}")
        # Return empty dict on error
        return {}


def parse_date_string(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse a date string from exiftool metadata.
    Handles various date formats and edge cases.

    Args:
        date_str: Date string from exiftool

    Returns:
        datetime object or None if parsing fails

    Examples:
        >>> parse_date_string('2023-10-15 14:30:45')
        datetime(2023, 10, 15, 14, 30, 45)
        >>> parse_date_string('2023-10-15 14:30:45.123')
        datetime(2023, 10, 15, 14, 30, 45)
        >>> parse_date_string('2023-10-15 14:30:45+05:00')
        datetime(2023, 10, 15, 14, 30, 45)
        >>> parse_date_string('2023-10-15 14:30:45-05:00')
        datetime(2023, 10, 15, 14, 30, 45)
    """
    if not date_str:
        return None

    # Trim any leading/trailing whitespace first
    date_str = date_str.strip()

    # Handle potential subsecond precision (e.g., .123 milliseconds)
    if '.' in date_str:
        date_str = date_str.split('.')[0]

    # Handle potential timezone offsets (both positive and negative)
    # Examples: +05:00, -05:00, +0000, -0800
    if '+' in date_str:
        date_str = date_str.split('+')[0]
    elif date_str.count('-') > 2:
        # Date format is YYYY-MM-DD, so 2 dashes are expected
        # If there are more than 2, the extra one(s) are likely timezone offset
        # '2023-10-15 14:30:45-05:00' -> split on last dash after the space
        space_idx = date_str.find(' ')
        if space_idx > 0:
            # Look for timezone offset after the time portion
            time_part = date_str[space_idx+1:]
            if '-' in time_part:
                # Split the time portion to remove timezone
                date_str = date_str[:space_idx+1] + time_part.split('-')[0]

    # Trim any trailing whitespace again after processing
    date_str = date_str.strip()

    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None


def open_directory(path: str) -> None:
    """Opens a directory in the default file explorer, cross-platform."""
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'darwin':
        subprocess.run(['open', path])
    else:  # Linux and other Unix-like OS
        try:
            subprocess.run(['xdg-open', path])
        except FileNotFoundError:
            print(f"Error: xdg-open is not available. Could not open directory {path}")


def parse_range(value: Optional[str]) -> List[int]:
    """
    Parses a range string (e.g., '2020-2023' or '3-6') into a list of integers.

    Args:
        value: String representing a single value or range (e.g., "2020", "2020-2023")

    Returns:
        List of integers in the range
    """
    if not value:
        return []
    if '-' in value and value.count('-') == 1 and not value.startswith('-'):
        start, end = map(int, value.split('-'))
        return list(range(start, end + 1))
    else:
        return [int(value)]


def get_move_warning_message() -> str:
    """
    Returns the warning message for move operations.
    This is shared between CLI and GUI to ensure consistency.

    Returns:
        str: The warning message to display to users
    """
    return (
        "⚠️  WARNING: MOVE MODE ⚠️\n\n"
        "You are about to MOVE files (not copy them).\n\n"
        "This operation will:\n"
        "• Remove files from their original location\n"
        "• Place them in the new organized structure\n"
        "• This action cannot be automatically undone"
    )


def confirm_move_operation_cli() -> bool:
    """
    Prompts the user for confirmation before performing move operations (CLI version).
    Default is Yes - pressing Enter without input confirms the operation.

    Returns:
        bool: True if user confirms, False otherwise
    """
    print("\n" + "=" * 60)
    print(get_move_warning_message())
    print("=" * 60 + "\n")

    while True:
        response = input("Continue with MOVE operation? [Y/n]: ").strip().lower()

        # Empty response (just pressing Enter) defaults to Yes
        if response == '' or response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            print("\nOperation Cancelled.\n")
            return False
        else:
            print("\nPlease enter 'Y' or Enter to confirm, 'n' to cancel.")
