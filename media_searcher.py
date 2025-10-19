import os
import argparse
import sys
import subprocess
from datetime import datetime

def open_directory(path):
    """Opens a directory in the default file explorer, cross-platform."""
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'darwin':
        subprocess.run(['open', path])
    else: # Linux and other Unix-like OS
        try:
            subprocess.run(['xdg-open', path])
        except FileNotFoundError:
            print(f"Error: xdg-open is not available. Could not open directory {path}")

def parse_range(value):
    """Parses a range string (e.g., '2020-2023') into a list of integers."""
    if not value:
        return []
    if '-' in value:
        start, end = map(int, value.split('-'))
        return list(range(start, end + 1))
    else:
        return [int(value)]

def search_media(search_dir, year_str=None, month_str=None, keywords=None, keyword_match='any', open_dirs=False):
    """
    Searches for media files in a directory structure based on year, month, and keywords.
    The keyword search is case-insensitive.
    """
    years_to_search = parse_range(year_str)
    months_to_search = parse_range(month_str)

    found_files = []
    for root, dirs, files in os.walk(search_dir):
        # Extract year and month from the path
        path_parts = root.split(os.sep)
        
        # Determine the year and month from the directory structure
        current_year = None
        current_month = None

        for part in path_parts:
            if len(part) == 4 and part.isdigit():
                current_year = int(part)
            if len(part) == 2 and part.isdigit() and 1 <= int(part) <= 12:
                current_month = int(part)

        # Filter by year
        if years_to_search and current_year not in years_to_search:
            continue

        # Filter by month
        if months_to_search and current_month not in months_to_search:
            continue

        # Filter by keywords
        if keywords:
            path_lower = root.lower()
            if keyword_match == 'any':
                if not any(k.lower() in path_lower for k in keywords):
                    continue
            elif keyword_match == 'all':
                if not all(k.lower() in path_lower for k in keywords):
                    continue

        for filename in files:
            found_files.append(os.path.join(root, filename))

    if found_files:
        print("\nFound files:")
        for f in found_files:
            print(f"  - {f}")

        if open_dirs:
            unique_dirs = set(os.path.dirname(f) for f in found_files)
            print("\nOpening directories containing matched files...")
            for directory in unique_dirs:
                print(f"  - Opening: {directory}")
                open_directory(directory)
    else:
        print("No files found matching the criteria.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Search for media files in a sorted directory.")
    parser.add_argument('search_dir', type=str, help='The directory to search in.')
    parser.add_argument('--year', '-y', type=str, help='The year or year range to search for (e.g., 2022, 2020-2023).')
    parser.add_argument('--month', '-m', type=str, help='The month or month range to search for (e.g., 1, 3-6).')
    parser.add_argument('--keyword', '-k', type=str, nargs='+', help='One or more keywords or event names to search for. The search is case-insensitive.')
    parser.add_argument('--keyword-match', type=str, choices=['any', 'all'], default='any', help='How to match keywords: \'any\' (default) or \'all\'.')
    parser.add_argument('--open-dirs', action='store_true', help='Open the directories containing the matched files in the file explorer.')

    args = parser.parse_args()

    search_media(args.search_dir, args.year, args.month, args.keyword, args.keyword_match, args.open_dirs)