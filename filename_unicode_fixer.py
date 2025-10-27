#!/usr/bin/env python3
"""
Unicode Filename Fixer - Special tool for fixing Unicode escape sequences in filenames
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class UnicodeFilenameFixer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.fixed_files: List[Tuple[str, str]] = []
        
    def decode_unicode_escape(self, filename: str) -> str:
        """Decode Unicode escape sequences like #U51b2#U950b#U7ebf to actual Chinese characters"""
        # Pattern to match #U followed by 4 hex digits
        pattern = r'#U([0-9a-fA-F]{4})'
        
        def replace_unicode_match(match):
            hex_code = match.group(1)
            try:
                # Convert hex to integer, then to Unicode character
                unicode_char = chr(int(hex_code, 16))
                return unicode_char
            except ValueError:
                return match.group(0)  # Return original if conversion fails
        
        # Replace all Unicode escape sequences
        decoded_name = re.sub(pattern, replace_unicode_match, filename)
        return decoded_name
    
    def fix_pathname(self, path: Path) -> bool:
        """Fix Unicode escape sequences in a single file or directory name"""
        original_name = path.name

        # Check if name contains Unicode escape sequences
        if not re.search(r'#U[0-9a-fA-F]{4}', original_name):
            return False

        # Decode the Unicode escape sequences
        new_name = self.decode_unicode_escape(original_name)

        # Skip if no change was made
        if new_name == original_name:
            return False

        # Create new path
        new_path = path.parent / new_name

        # Check if new name already exists
        if new_path.exists():
            print(f"Warning: Target name already exists: {new_name}")
            return False

        try:
            # Rename the file or directory
            path.rename(new_path)
            self.fixed_files.append((str(path), str(new_path)))
            item_type = "directory" if path.is_dir() else "filename"
            print(f"Fixed {item_type}: {original_name} -> {new_name}")
            return True
        except Exception as e:
            item_type = "directory" if path.is_dir() else "filename"
            print(f"Error renaming {item_type} {original_name}: {e}")
            return False

    def fix_filename(self, file_path: Path) -> bool:
        """Fix Unicode escape sequences in a single filename (backward compatibility)"""
        return self.fix_pathname(file_path)
    
    def scan_and_fix_directory(self, target_path: Optional[str] = None, fix_folders: bool = True):
        """Scan directory and fix Unicode escape sequences in filenames and optionally folder names"""
        scan_path = Path(target_path) if target_path else self.root_path

        print(f"Scanning directory for Unicode escape sequences: {scan_path}")
        print("-" * 60)

        items_processed = 0
        items_fixed = 0

        for root, dirs, files in os.walk(scan_path):

            # Process directories if enabled
            if fix_folders:
                for dirname in dirs[:]:
                    dir_path = Path(root) / dirname
                    items_processed += 1

                    if self.fix_pathname(dir_path):
                        items_fixed += 1
                        # Update dirs list to reflect the new name for further traversal
                        dirs[dirs.index(dirname)] = self.decode_unicode_escape(dirname)

            # Process files
            for filename in files:
                file_path = Path(root) / filename
                items_processed += 1

                if self.fix_pathname(file_path):
                    items_fixed += 1

        print("\n" + "=" * 60)
        print(f"Scan completed!")
        print(f"Items processed: {items_processed}")
        print(f"Items with Unicode escape sequences fixed: {items_fixed}")

        if self.fixed_files:
            print(f"\nFixed items:")
            for old_path, new_path in self.fixed_files:
                print(f"  {old_path} -> {new_path}")
        else:
            print("No Unicode escape sequences found in filenames or folder names.")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Unicode Filename and Folder Fixer Tool')
    parser.add_argument('path', nargs='?', default='.', help='Directory path to scan (default: current directory)')
    parser.add_argument('--no-folders', action='store_true', help='Only fix filenames, skip folder names')

    args = parser.parse_args()

    target_path = args.path
    fix_folders = not args.no_folders

    # Convert to absolute path
    target_path = os.path.abspath(target_path)

    if not os.path.exists(target_path):
        print(f"Error: Path '{target_path}' does not exist!")
        sys.exit(1)

    if not os.path.isdir(target_path):
        print(f"Error: '{target_path}' is not a directory!")
        sys.exit(1)

    print("Unicode Filename and Folder Fixer Tool")
    print("=" * 50)
    print("This tool fixes Unicode escape sequences in filenames and folder names.")
    print("Example: #U51b2#U950b#U7ebf.txt -> 冲锋线.txt")
    print("Example: #U6d4b#U8bd5#U6587#U4ef6#U5939 -> 测试文件夹")
    print()

    fixer = UnicodeFilenameFixer(target_path)
    fixer.scan_and_fix_directory(fix_folders=fix_folders)


if __name__ == "__main__":
    main()