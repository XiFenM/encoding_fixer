#!/usr/bin/env python3
"""
Encoding Fixer - Main entry point
"""

import sys
import os
from encoding_fixer import EncodingFixer


def main():
    print("Encoding Fixer Tool")
    print("=" * 30)
    print("This tool scans for and fixes filename and content encoding issues.")
    print()
    
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = input("Enter directory path to scan (default: current directory): ").strip()
        if not target_path:
            target_path = "."
    
    # Convert to absolute path
    target_path = os.path.abspath(target_path)
    
    if not os.path.exists(target_path):
        print(f"Error: Path '{target_path}' does not exist!")
        sys.exit(1)
    
    if not os.path.isdir(target_path):
        print(f"Error: '{target_path}' is not a directory!")
        sys.exit(1)
    
    print(f"Starting scan in: {target_path}")
    print()
    
    fixer = EncodingFixer(target_path)
    fixer.scan_directory()


if __name__ == "__main__":
    main()
