#!/usr/bin/env python3

import os
import re
from pathlib import Path

def cleanup_duplicate_files(directory):
    """
    Clean up duplicate files in the specified directory.
    Keep only files with _1 suffix when there are multiple versions.
    If there's no _1 version, keep the original file without number.
    """
    directory = Path(directory)

    # Dictionary to group files by their base name
    file_groups = {}

    # Pattern to match files with numbered suffixes
    pattern = re.compile(r'^(.+)_(\d+)(\.[^.]+)$')

    # First pass: collect all files and group them
    for file_path in directory.iterdir():
        if file_path.is_file():
            filename = file_path.name
            match = pattern.match(filename)

            if match:
                # File has numbered suffix
                base_name = match.group(1)
                number = int(match.group(2))
                extension = match.group(3)
                base_key = f"{base_name}{extension}"

                if base_key not in file_groups:
                    file_groups[base_key] = {'original': None, 'numbered': {}}

                file_groups[base_key]['numbered'][number] = file_path
            else:
                # Check if this could be the original file for a numbered series
                base_key = filename
                if base_key not in file_groups:
                    file_groups[base_key] = {'original': None, 'numbered': {}}

                file_groups[base_key]['original'] = file_path

    # Second pass: identify files to delete
    files_to_delete = []
    files_kept = []

    for base_key, group in file_groups.items():
        numbered_files = group['numbered']
        original_file = group['original']

        if len(numbered_files) > 0:
            # There are numbered versions
            if 1 in numbered_files:
                # Keep the _1 version, delete all others
                files_kept.append(numbered_files[1])
                for num, file_path in numbered_files.items():
                    if num != 1:
                        files_to_delete.append(file_path)
                # If there's an original file, delete it too
                if original_file:
                    files_to_delete.append(original_file)
            else:
                # No _1 version, keep the original if it exists, otherwise keep the lowest numbered
                if original_file:
                    files_kept.append(original_file)
                    # Delete all numbered versions
                    for file_path in numbered_files.values():
                        files_to_delete.append(file_path)
                else:
                    # Keep the lowest numbered version
                    min_num = min(numbered_files.keys())
                    files_kept.append(numbered_files[min_num])
                    for num, file_path in numbered_files.items():
                        if num != min_num:
                            files_to_delete.append(file_path)

    # Show what will be deleted
    print(f"Found {len(files_to_delete)} duplicate files to delete:")
    for file_path in files_to_delete:
        print(f"  DELETE: {file_path.name}")

    print(f"\nKeeping {len(files_kept)} files:")
    for file_path in files_kept:
        print(f"  KEEP: {file_path.name}")

    # Proceed with deletion automatically
    if files_to_delete:
        print(f"\nProceeding to delete {len(files_to_delete)} files...")
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                deleted_count += 1
                if deleted_count % 1000 == 0:  # Print progress every 1000 files
                    print(f"Deleted {deleted_count} files so far...")
            except Exception as e:
                print(f"Error deleting {file_path.name}: {e}")

        print(f"\nSuccessfully deleted {deleted_count} duplicate files.")
    else:
        print("No duplicate files found to delete.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python cleanup_duplicates.py <attachments_directory>")
        print("Example: python cleanup_duplicates.py downloads/guild_123456/channel_name_789/attachments")
        sys.exit(1)

    attachments_dir = sys.argv[1]
    cleanup_duplicate_files(attachments_dir)