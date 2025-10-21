#!/usr/bin/env python3
"""
Media Searcher - Find media files by date, keywords, and ratings.

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

import os
import argparse
import sys
import subprocess

# Handle imports whether run as module or script
try:
    from media_utils import open_directory, parse_range
    from __version__ import __version__
except ImportError:
    from src.media_utils import open_directory, parse_range
    from src.__version__ import __version__

def validate_rating(value):
    """Validates that a rating value is an integer between -1 and 5."""
    try:
        rating = int(value)
        if -1 <= rating <= 5:
            return rating
        else:
            raise argparse.ArgumentTypeError(f"Rating must be between -1 and 5.")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid rating value: {value}")

def search_media(search_dir, year_str=None, month_str=None, keywords=None, keyword_match='any', rating_str=None, open_dirs=False):
    """
    Searches for media files in a directory structure based on year, month, keywords (in path and metadata), and rating.
    The keyword search is case-insensitive.

    Optimized version with improved filtering logic and better performance.
    """
    years_to_search = parse_range(year_str)
    months_to_search = parse_range(month_str)
    ratings_to_search = parse_range(rating_str) if rating_str else []
    if ratings_to_search:
        for r in ratings_to_search:
            validate_rating(r)

    found_files = []

    print(f"Searching in: {search_dir}")
    if years_to_search:
        print(f"Year filter: {years_to_search}")
    if months_to_search:
        print(f"Month filter: {months_to_search}")
    if keywords:
        print(f"Keyword filter: {keywords} (match: {keyword_match})")
    if ratings_to_search:
        print(f"Rating filter: {ratings_to_search}")

    # First, filter by directory structure (year, month, and keyword in path)
    preliminary_files = []
    skipped_dirs = 0

    for root, dirs, files in os.walk(search_dir):
        path_parts = root.split(os.sep)
        current_year, current_month = None, None
        for part in path_parts:
            if len(part) == 4 and part.isdigit():
                current_year = int(part)
            if len(part) == 2 and part.isdigit() and 1 <= int(part) <= 12:
                current_month = int(part)

        # Early directory filtering - skip entire directories if they don't match
        if years_to_search and current_year and current_year not in years_to_search:
            dirs[:] = []  # Don't recurse into subdirectories
            skipped_dirs += 1
            continue

        if months_to_search and current_month and current_month not in months_to_search:
            dirs[:] = []  # Don't recurse into subdirectories
            skipped_dirs += 1
            continue

        path_lower = root.lower()
        # For 'all' keyword match in path, skip directories that don't contain all keywords
        if keywords and keyword_match == 'all' and not all(k.lower() in path_lower for k in keywords):
            # Check if any files in this directory might still match via metadata
            # For now, we'll still include them but this is a conservative approach
            pass

        for filename in files:
            # Skip hidden files (files starting with .)
            if not filename.startswith('.'):
                preliminary_files.append(os.path.join(root, filename))

    if skipped_dirs > 0:
        print(f"Skipped {skipped_dirs} directories based on year/month filters.")

    # Now, filter by metadata (rating and keywords)
    if ratings_to_search or keywords:
        exiftool_cmd = ['exiftool', '-r', '-if']
        conditions = []
        if ratings_to_search:
            conditions.append(' or '.join([f'$Rating == {r}' for r in ratings_to_search]))
        
        if keywords:
            op = 'or' if keyword_match == 'any' else 'and'
            keyword_conditions = f' {op} '.join([f'$Keywords =~ /{k}/i' for k in keywords])
            conditions.append(f'({keyword_conditions})')

        exiftool_cmd.append(' and '.join(conditions))
        exiftool_cmd.extend(['-p', '$directory/$filename'])
        exiftool_cmd.extend(preliminary_files) # Search only within the preliminary files

        try:
            result = subprocess.run(exiftool_cmd, capture_output=True, text=True, check=True)
            found_files.extend(result.stdout.strip().split('\n'))
        except FileNotFoundError:
            print("Error: exiftool is not installed or not in your PATH.")
            return
        except subprocess.CalledProcessError as e:
            # It's normal for exiftool to exit with an error if no files match the condition
            pass
    else:
        found_files = preliminary_files

    # Also include files that match keywords in their path, even if no metadata match
    if keywords:
        for f in preliminary_files:
            path_lower = f.lower()
            if keyword_match == 'any' and any(k.lower() in path_lower for k in keywords):
                if f not in found_files:
                    found_files.append(f)
            elif keyword_match == 'all' and all(k.lower() in path_lower for k in keywords):
                if f not in found_files:
                    found_files.append(f)

    if found_files:
        print("\nFound files:")
        for f in found_files:
            print(f"  - {f}")

        if open_dirs:
            # Get directories that directly contain matched files
            dirs_with_files = set(os.path.dirname(f) for f in found_files)

            # Filter out directories that only contain subdirectories with matches
            # but no actual matched files themselves
            dirs_to_open = set()
            for directory in dirs_with_files:
                # Check if this directory directly contains any matched files
                has_direct_files = any(os.path.dirname(f) == directory for f in found_files)
                if has_direct_files:
                    dirs_to_open.add(directory)

            print("\nOpening directories containing matched files...")
            for directory in sorted(dirs_to_open):
                print(f"  - Opening: {directory}")
                open_directory(directory)
    else:
        print("No files found matching the criteria.")


def main():
    """Main entry point for the media searcher command-line interface."""
    parser = argparse.ArgumentParser(
        description="Search for media files in a sorted directory.",
        epilog=f"Illuminate Media Organizer v{__version__}"
    )
    parser.add_argument('search_dir', type=str, help='The directory to search in.')
    parser.add_argument('--year', '-y', type=str, help='The year or year range to search for (e.g., 2022, 2020-2023).')
    parser.add_argument('--month', '-m', type=str, help='The month or month range to search for (e.g., 1, 3-6).')
    parser.add_argument('--keyword', '-k', type=str, nargs='+', help='One or more keywords to search for in path or metadata. The search is case-insensitive.')
    parser.add_argument('--keyword-match', type=str, choices=['any', 'all'], default='any', help='How to match keywords: \'any\' (default) or \'all\'.')
    parser.add_argument('--rating', '-r', type=str, help='Search for a specific rating or range. Mutually exclusive with --rejected and --picked.')
    parser.add_argument('--rejected', '-R', action='store_true', help='Search for rejected files (rating of -1). Mutually exclusive with --rating and --picked.')
    parser.add_argument('--picked', '-P', action='store_true', help='Search for picked files (rating of 0-5). Mutually exclusive with --rating and --rejected.')
    parser.add_argument('--open-dirs', action='store_true', help='Open the directories containing the matched files in the file explorer.')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()

    if args.rejected and args.picked:
        print("Warning: --rejected and --picked flags should not be used together. This combination is redundant.")
        sys.exit(1)

    if args.rating and (args.rejected or args.picked):
        print("Warning: --rating should not be used with --rejected or --picked. Provide either a rating or a status flag.")
        sys.exit(1)

    rating_str = args.rating
    if args.rejected:
        rating_str = '-1'
    elif args.picked:
        rating_str = '0-5'

    search_media(args.search_dir, args.year, args.month, args.keyword, args.keyword_match, rating_str, args.open_dirs)


if __name__ == '__main__':
    main()