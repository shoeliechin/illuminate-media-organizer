#!/usr/bin/env python3
"""
Shared utilities for the Media Organizer project.
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
import json


def is_exiftool_installed():
    """Check if exiftool is installed and available in the system's PATH."""
    try:
        subprocess.run(['exiftool', '-ver'], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_pictures_directory():
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
            except:
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
            except:
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


def get_creation_dates_batch(file_paths, verbose=False):
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
                    # Handle potential timezone offsets or other suffixes
                    if '.' in date_str:
                        date_str = date_str.split('.')[0]
                    if '+' in date_str:
                        date_str = date_str.split('+')[0]

                    try:
                        creation_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        break
                    except ValueError:
                        continue  # Try the next tag if parsing fails

            results[source_file] = creation_date

        return results

    except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError) as e:
        if verbose:
            print(f"Error processing batch metadata: {e}")
        # Return empty dict on error
        return {}


def parse_date_string(date_str):
    """
    Parse a date string from exiftool metadata.
    Handles various date formats and edge cases.

    Args:
        date_str: Date string from exiftool

    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None

    # Handle potential timezone offsets or other suffixes
    if '.' in date_str:
        date_str = date_str.split('.')[0]
    if '+' in date_str:
        date_str = date_str.split('+')[0]

    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None


def open_directory(path):
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


def parse_range(value):
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
