import os
import shutil
import subprocess
import argparse
import json
from datetime import datetime

def is_exiftool_installed():
    """Check if exiftool is installed and available in the system's PATH."""
    try:
        # Use subprocess.run to execute 'exiftool -ver'
        # Capture output to prevent it from printing to the console
        subprocess.run(['exiftool', '-ver'], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_creation_date(file_path):
    """
    Get the creation date of a media file using exiftool.
    It checks multiple tags to find the best available date.
    """
    # Tags to check in order of preference
    date_tags = [
        'SubSecCreateDate', 'SubSecDateTimeOriginal', 'CreateDate', 
        'DateTimeOriginal', 'MediaCreateDate', 'TrackCreateDate', 'ModifyDate'
    ]
    
    # Build the command to run
    command = ['exiftool', '-json', '-d', '%Y-%m-%d %H:%M:%S']
    command.extend([f'-{tag}' for tag in date_tags])
    command.append(file_path)

    try:
        # Execute exiftool command
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        metadata = json.loads(result.stdout)[0]

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
                    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue # Try the next tag if parsing fails
        
        # If no date tags are found, return None
        return None

    except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError) as e:
        print(f"  - Could not process metadata for {os.path.basename(file_path)}: {e}")
        # If an error occurs, return None
        return None
        

def sort_media_files(source_dir, dest_dir, copy_files=False, dry_run=False, fallback_to_file_time=None):
    """
    Sorts media files from a source directory to a destination directory
    based on their creation date. The destination directory structure
    will be YYYY/MM.
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

    skipped_files = []

    # Walk through the source directory
    for root, _, files in os.walk(source_dir):
        for filename in files:
            source_path = os.path.join(root, filename)
            print(f"\nProcessing: {filename}")

            # Get creation date
            creation_date = get_creation_date(source_path)

            if not creation_date:
                if fallback_to_file_time == 'created':
                    stat_info = os.stat(source_path)
                    creation_date = datetime.fromtimestamp(stat_info.st_ctime)
                elif fallback_to_file_time == 'modified':
                    stat_info = os.stat(source_path)
                    creation_date = datetime.fromtimestamp(stat_info.st_mtime)
                else:
                    skipped_files.append(filename)
                    print(f"  - Could not determine creation date for {filename}. Skipping.")
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
                except Exception as e:
                    print(f"  - ERROR: Could not move/copy file. {e}")
    
    print("\n--- Sorting complete! ---")
    if dry_run:
        print("--- DRY RUN MODE: No changes were made. ---")

    if skipped_files:
        print("\nThe following files were skipped because their creation date could not be determined:")
        for filename in skipped_files:
            print(f"  - {filename}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Sort media files using exiftool.")
    parser.add_argument('source_dir', type=str, help='The source directory with media files.')
    parser.add_argument('dest_dir', type=str, help='The destination directory for sorted files.')
    parser.add_argument('--copy', action='store_true', help='Copy files instead of moving them.')
    parser.add_argument('--dry-run', action='store_true', help='Simulate the process without moving/copying files.')
    parser.add_argument('--fallback-to-file-time', type=str, choices=['created', 'modified'], help='Use file creation or modification time if EXIF data is not available.')
    
    args = parser.parse_args()

    sort_media_files(args.source_dir, args.dest_dir, args.copy, args.dry_run, args.fallback_to_file_time)
