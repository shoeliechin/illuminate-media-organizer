#!/usr/bin/env python3

import os
import shutil
import argparse
from datetime import datetime

# Handle imports whether run as module or script
try:
    from media_utils import is_exiftool_installed, get_creation_dates_batch
except ImportError:
    from src.media_utils import is_exiftool_installed, get_creation_dates_batch
        

def sort_media_files(source_dir, dest_dir, copy_files=False, dry_run=False, fallback_to_file_time=None):
    """
    Sorts media files from a source directory to a destination directory
    based on their creation date. The destination directory structure
    will be YYYY/MM.

    Optimized version that batches exiftool calls for much better performance.
    """
    if not is_exiftool_installed():
        print("Error: exiftool is not installed or not in your system's PATH.")
        print("Please install it from https://exiftool.org/")
        return

    print(f"Starting media sort from '{source_dir}' to '{dest_dir}'")
    print(f"Mode: {'Copy' if copy_files else 'Move'}")
    if dry_run:
        print("--- DRY RUN MODE: No files will be moved or copied. ---")

    # Ensure the destination directory exists
    if not dry_run:
        os.makedirs(dest_dir, exist_ok=True)

    # First pass: Collect all file paths
    print("\nScanning directory for media files...")
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Sort media files using exiftool.")
    parser.add_argument('source_dir', type=str, help='The source directory with media files.')
    parser.add_argument('dest_dir', type=str, help='The destination directory for sorted files.')
    parser.add_argument('--copy', action='store_true', help='Copy files instead of moving them.')
    parser.add_argument('--dry-run', action='store_true', help='Simulate the process without moving/copying files.')
    parser.add_argument('--fallback-to-file-time', type=str, choices=['created', 'modified'], help='Use file creation or modification time if EXIF data is not available.')
    
    args = parser.parse_args()

    sort_media_files(args.source_dir, args.dest_dir, args.copy, args.dry_run, args.fallback_to_file_time)
