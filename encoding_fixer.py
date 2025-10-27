#!/usr/bin/env python3
"""
Encoding Fixer - Scan and fix filename and content encoding issues
"""

import os
import sys
import chardet
import codecs
from pathlib import Path
from typing import List, Tuple, Optional


class EncodingFixer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.problematic_files: List[Tuple[str, str]] = []  # (old_path, new_path)
        self.encoding_issues: List[Tuple[str, str, str]] = []  # (file_path, old_encoding, new_encoding)
        
    def detect_encoding(self, file_path: Path) -> Optional[str]:
        """Detect file encoding using chardet"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                if not raw_data:
                    return None
                    
                result = chardet.detect(raw_data)
                return result.get('encoding')
        except Exception as e:
            print(f"Error detecting encoding for {file_path}: {e}")
            return None
    
    def is_filename_valid(self, filename: str) -> bool:
        """Check if filename contains only valid characters"""
        try:
            filename.encode('ascii')
            return True
        except UnicodeEncodeError:
            return False
    
    def fix_filename_encoding(self, file_path: Path) -> Optional[Path]:
        """Try to fix filename encoding issues"""
        filename = file_path.name
        
        # If filename is already valid, return None
        if self.is_filename_valid(filename):
            return None
        
        print(f"Attempting to fix filename: {filename}")
        
        # Common mojibake patterns and their fixes
        mojibake_fixes = {
            'æ–‡ä»¶': '文件',  # Common mojibake for Chinese characters
            'Ã©': 'é',  # Common mojibake for é
            'Ã¨': 'è',  # Common mojibake for è
            'Ã ': 'à',  # Common mojibake for à
            'Ã±': 'ñ',  # Common mojibake for ñ
            'Ã¤': 'ä',  # Common mojibake for ä
            'Ã¶': 'ö',  # Common mojibake for ö
            'Ã¼': 'ü',  # Common mojibake for ü
        }
        
        # Try direct mojibake fixes first
        new_filename = filename
        for mojibake, correct in mojibake_fixes.items():
            new_filename = new_filename.replace(mojibake, correct)
        
        # If we made changes, try to rename
        if new_filename != filename:
            new_path = file_path.parent / new_filename
            if not new_path.exists():
                try:
                    file_path.rename(new_path)
                    self.problematic_files.append((str(file_path), str(new_path)))
                    print(f"Fixed filename: {filename} -> {new_filename}")
                    return new_path
                except Exception as e:
                    print(f"Error renaming {filename}: {e}")
                    return None
        
        # Try different encoding combinations for more complex cases
        encodings_to_try = [
            ('latin1', 'utf-8'),
            ('cp1252', 'utf-8'),
            ('gbk', 'utf-8'),
            ('gb2312', 'utf-8'),
            ('big5', 'utf-8'),
        ]
        
        for from_enc, to_enc in encodings_to_try:
            try:
                # Try to decode from one encoding and re-encode to UTF-8
                decoded_bytes = filename.encode('latin1')  # First get raw bytes
                decoded_name = decoded_bytes.decode(from_enc, errors='ignore')
                
                # Create new path
                new_path = file_path.parent / decoded_name
                
                # Check if new filename is valid and doesn't already exist
                if decoded_name and self.is_filename_valid(decoded_name) and not new_path.exists():
                    try:
                        file_path.rename(new_path)
                        self.problematic_files.append((str(file_path), str(new_path)))
                        print(f"Fixed filename: {filename} -> {decoded_name}")
                        return new_path
                    except Exception as e:
                        print(f"Error renaming {filename}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Failed encoding conversion {from_enc}->UTF-8 for {filename}: {e}")
                continue
        
        print(f"Could not fix filename: {filename}")
        return None
    
    def fix_file_content_encoding(self, file_path: Path) -> bool:
        """Fix content encoding issues in text files"""
        if not file_path.is_file():
            return False
            
        # Skip binary files
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(1024)
                if b'\0' in sample:
                    return False  # Binary file
        except:
            return False
        
        # Detect current encoding
        detected_encoding = self.detect_encoding(file_path)
        if not detected_encoding or detected_encoding.lower() == 'utf-8':
            return False
        
        try:
            # Read file with detected encoding
            with open(file_path, 'r', encoding=detected_encoding, errors='ignore') as f:
                content = f.read()
            
            # Write back as UTF-8
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.encoding_issues.append((str(file_path), detected_encoding, 'utf-8'))
            print(f"Fixed content encoding: {file_path.name} ({detected_encoding} -> UTF-8)")
            return True
            
        except Exception as e:
            print(f"Error fixing content encoding for {file_path}: {e}")
            return False
    
    def scan_directory(self, target_path: Optional[str] = None):
        """Scan directory for encoding issues"""
        scan_path = Path(target_path) if target_path else self.root_path
        
        print(f"Scanning directory: {scan_path}")
        print("-" * 50)
        
        for root, dirs, files in os.walk(scan_path):
            for filename in files:
                file_path = Path(root) / filename
                
                # Check filename encoding
                if not self.is_filename_valid(filename):
                    print(f"Found problematic filename: {file_path}")
                    self.fix_filename_encoding(file_path)
                
                # Fix content encoding for txt files
                if file_path.suffix.lower() == '.txt':
                    self.fix_file_content_encoding(file_path)
        
        print("\n" + "=" * 50)
        print("Scan completed!")
        
        if self.problematic_files:
            print(f"\nFixed {len(self.problematic_files)} filename encoding issues:")
            for old, new in self.problematic_files:
                print(f"  {old} -> {new}")
        
        if self.encoding_issues:
            print(f"\nFixed {len(self.encoding_issues)} content encoding issues:")
            for file_path, old_enc, new_enc in self.encoding_issues:
                print(f"  {file_path}: {old_enc} -> {new_enc}")
        
        if not self.problematic_files and not self.encoding_issues:
            print("No encoding issues found!")


def main():
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = input("Enter directory path to scan (default: current directory): ").strip()
        if not target_path:
            target_path = "."
    
    if not os.path.exists(target_path):
        print(f"Error: Path '{target_path}' does not exist!")
        sys.exit(1)
    
    fixer = EncodingFixer(target_path)
    fixer.scan_directory()


if __name__ == "__main__":
    main()