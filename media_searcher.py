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
    if '-' in value and value.count('-') == 1 and not value.startswith('-'):
        start, end = map(int, value.split('-'))
        return list(range(start, end + 1))
    else:
        return [int(value)]

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
    """
    years_to_search = parse_range(year_str)
    months_to_search = parse_range(month_str)
    ratings_to_search = parse_range(rating_str) if rating_str else []
    if ratings_to_search:
        for r in ratings_to_search:
            validate_rating(r)

    found_files = []
    
    # First, filter by directory structure (year, month, and keyword in path)
    preliminary_files = []
    for root, dirs, files in os.walk(search_dir):
        path_parts = root.split(os.sep)
        current_year, current_month = None, None
        for part in path_parts:
            if len(part) == 4 and part.isdigit():
                current_year = int(part)
            if len(part) == 2 and part.isdigit() and 1 <= int(part) <= 12:
                current_month = int(part)

        if (years_to_search and current_year not in years_to_search) or \
           (months_to_search and current_month not in months_to_search):
            continue

        path_lower = root.lower()
        if keywords and keyword_match == 'any' and not any(k.lower() in path_lower for k in keywords):
            pass # Don't skip yet, as keyword might be in metadata
        elif keywords and keyword_match == 'all' and not all(k.lower() in path_lower for k in keywords):
            continue

        for filename in files:
            preliminary_files.append(os.path.join(root, filename))

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
    parser.add_argument('--keyword', '-k', type=str, nargs='+', help='One or more keywords to search for in path or metadata. The search is case-insensitive.')
    parser.add_argument('--keyword-match', type=str, choices=['any', 'all'], default='any', help='How to match keywords: \'any\' (default) or \'all\'.')
    parser.add_argument('--rating', '-r', type=str, help='Search for a specific rating or range. Mutually exclusive with --rejected and --picked.')
    parser.add_argument('--rejected', '-R', action='store_true', help='Search for rejected files (rating of -1). Mutually exclusive with --rating and --picked.')
    parser.add_argument('--picked', '-P', action='store_true', help='Search for picked files (rating of 0-5). Mutually exclusive with --rating and --rejected.')
    parser.add_argument('--open-dirs', action='store_true', help='Open the directories containing the matched files in the file explorer.')

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