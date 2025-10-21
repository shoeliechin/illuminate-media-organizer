#!/usr/bin/env python3
"""
Media Sorter - Organize media files by creation date into YYYY/MM structure.

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
import shutil
import argparse
from datetime import datetime

# Handle imports whether run as module or script
try:
    from media_utils import is_exiftool_installed, get_creation_dates_batch, confirm_move_operation_cli
    from __version__ import __version__
except ImportError:
    from src.media_utils import is_exiftool_installed, get_creation_dates_batch, confirm_move_operation_cli
    from src.__version__ import __version__
        

def sort_media_files(source_dir, dest_dir, copy_files=False, dry_run=False, fallback_to_file_time=None, skip_confirmation=False):
    """
    Sorts media files from a source directory to a destination directory
    based on their creation date. The destination directory structure
    will be YYYY/MM.

    Optimized version that batches exiftool calls for much better performance.

    Args:
        source_dir: Source directory containing media files
        dest_dir: Destination directory for sorted files
        copy_files: If True, copy files instead of moving them
        dry_run: If True, simulate without making changes
        fallback_to_file_time: Use file time if EXIF unavailable ('created' or 'modified')
        skip_confirmation: If True, skip move confirmation (for GUI use)
    """
    if not is_exiftool_installed():
        print("Error: exiftool is not installed or not in your system's PATH.")
        print("Please install it from https://exiftool.org/")
        return

    # Confirm move operation if not in copy mode and not dry run
    if not copy_files and not dry_run and not skip_confirmation:
        if not confirm_move_operation_cli():
            return

    print(f"\nStarting media sort from '{source_dir}' to '{dest_dir}'")
    print(f"Mode: {'Copy' if copy_files else 'Move'}\n")
    if dry_run:
        print("--- DRY RUN MODE: No files will be moved or copied. ---")

    # Ensure the destination directory exists
    if not dry_run:
        os.makedirs(dest_dir, exist_ok=True)

    # First pass: Collect all file paths
    print("Scanning directory for media files...")
    all_file_paths = []
    for root, _, files in os.walk(source_dir):
        for filename in files:
            # Skip hidden files
            if not filename.startswith('.'):
                source_path = os.path.join(root, filename)
                all_file_paths.append(source_path)

    if not all_file_paths:
        print("No files found to process.")
        return

    print(f"Found {len(all_file_paths)} files to process.")
    print("Reading metadata (this may take a moment)...")

    # Batch process all files at once - MUCH faster than individual calls
    creation_dates = get_creation_dates_batch(all_file_paths, verbose=True)

    print("\nProcessing files...")
    skipped_files = []
    processed_count = 0

    # Second pass: Process each file with its pre-fetched metadata
    for source_path in all_file_paths:
        filename = os.path.basename(source_path)
        print(f"\nProcessing: {filename}")

        # Get creation date from batch results
        creation_date = creation_dates.get(source_path)

        if not creation_date:
            if fallback_to_file_time == 'created':
                stat_info = os.stat(source_path)
                creation_date = datetime.fromtimestamp(stat_info.st_ctime)
                print(f"  - Using file creation time as fallback")
            elif fallback_to_file_time == 'modified':
                stat_info = os.stat(source_path)
                creation_date = datetime.fromtimestamp(stat_info.st_mtime)
                print(f"  - Using file modification time as fallback")
            else:
                skipped_files.append(filename)
                print(f"  - Could not determine creation date. Skipping.")
                continue

        # Create year and month directories
        year = creation_date.strftime('%Y')
        month = creation_date.strftime('%m')

        target_dir = os.path.join(dest_dir, year, month)

        if not dry_run:
            os.makedirs(target_dir, exist_ok=True)

        target_path = os.path.join(target_dir, filename)

        # Avoid overwriting files
        counter = 1
        base, ext = os.path.splitext(filename)
        while os.path.exists(target_path):
            target_path = os.path.join(target_dir, f"{base}_{counter}{ext}")
            counter += 1

        # Move or copy the file
        action = "Copying" if copy_files else "Moving"
        print(f"  - {action} to: {os.path.relpath(target_path, dest_dir)}")

        if not dry_run:
            try:
                if copy_files:
                    shutil.copy2(source_path, target_path)
                else:
                    shutil.move(source_path, target_path)
                processed_count += 1
            except Exception as e:
                print(f"  - ERROR: Could not move/copy file. {e}")
        else:
            processed_count += 1

    print(f"\n--- Sorting complete! Processed {processed_count}/{len(all_file_paths)} files ---")
    if dry_run:
        print("--- DRY RUN MODE: No changes were made. ---")

    if skipped_files:
        print(f"\n{len(skipped_files)} file(s) were skipped because their creation date could not be determined:")
        for filename in skipped_files[:10]:  # Show first 10
            print(f"  - {filename}")
        if len(skipped_files) > 10:
            print(f"  ... and {len(skipped_files) - 10} more")


def main():
    """Main entry point for the media sorter command-line interface."""
    parser = argparse.ArgumentParser(
        description="Sort media files using exiftool.",
        epilog=f"Illuminate Media Organizer v{__version__}"
    )
    parser.add_argument('source_dir', type=str, help='The source directory with media files.')
    parser.add_argument('dest_dir', type=str, help='The destination directory for sorted files.')
    parser.add_argument('--copy', action='store_true', help='Copy files instead of moving them.')
    parser.add_argument('--dry-run', action='store_true', help='Simulate the process without moving/copying files.')
    parser.add_argument('--fallback-to-file-time', type=str, choices=['created', 'modified'], help='Use file creation or modification time if EXIF data is not available.')
    parser.add_argument('-y', '--yes', action='store_true', help='Automatically confirm move operation without prompting (non-interactive mode).')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()

    # If --yes flag is provided, skip confirmation
    skip_confirmation = args.yes
    sort_media_files(args.source_dir, args.dest_dir, args.copy, args.dry_run, args.fallback_to_file_time, skip_confirmation)
    print()


if __name__ == '__main__':
    main()
