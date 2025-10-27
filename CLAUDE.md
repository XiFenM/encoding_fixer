# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python encoding fixer toolkit that handles filename and content encoding issues, particularly for Chinese text processing. The project uses UV package manager and requires Python 3.11+.

## Common Commands

### Development Setup
```bash
# Install dependencies using UV package manager
uv sync

# Run the main encoding fixer tool
uv run main.py [directory_path]

# Run Unicode filename fixer
uv run filename_unicode_fixer.py [directory_path] [--no-folders]

# Run file comparison tool
uv run file_comparison.py
```

### Testing
```bash
# Test encoding fixer with sample files
uv run main.py test_files/

# Test Unicode filename fixer
uv run filename_unicode_fixer.py test_folder_unicode/
```

## Architecture

### Core Components

1. **encoding_fixer.py**: Main encoding detection and conversion engine
   - Uses chardet for encoding detection
   - Handles mojibake pattern recognition and repair
   - Converts file content to UTF-8
   - Key method: `fix_file_encoding()` processes individual files

2. **filename_unicode_fixer.py**: Unicode escape sequence decoder
   - Decodes patterns like `#U51b2#U950b#U7ebf` to actual Unicode characters
   - Handles both files and directories
   - Key method: `decode_unicode_escape()` performs the conversion

3. **file_comparison.py**: Directory comparison utility
   - Compares TXT file contents between two directories
   - Uses MD5 hashing for content comparison
   - Supports PDF file size comparison
   - Fixed paths: compares `chinese_old/` vs `chinese/`

### Design Patterns

- **Class-based architecture**: Each tool is encapsulated in its own class
- **Path handling**: Uses `pathlib.Path` for cross-platform compatibility
- **Error handling**: Graceful handling of encoding errors and file operations
- **Progress reporting**: Detailed console output during processing

### Key Dependencies

- **chardet**: Character encoding detection
- **pathlib**: Modern path handling
- **argparse**: Command-line interface

## Important Notes

- Always use `uv run` prefix when executing Python scripts in this project
- The tools modify files in-place - ensure backups before running on important data
- Unicode filename fixer processes directories recursively by default
- File comparison tool has hardcoded paths that may need adjustment for different environments