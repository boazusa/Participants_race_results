#!/usr/bin/env python3
"""
Copy project to git directory, excluding sensitive files and folders.
"""

import os
import shutil
from pathlib import Path

# Source and destination paths
SOURCE_DIR = Path(r"C:\Users\USER\Documents\Python\running_records\running_records_windsurf")
DEST_DIR = Path(r"C:\Users\USER\Documents\Python\running_records\best_results_git")

# Files and folders to exclude
EXCLUDE = {
    "login_info",
    ".benchmarks",
    ".pytest_cache",
    "__pycache__",
    "Screenshots",
    "run_history.json",
    ".git",
    ".idea",
    ".vscode",
    ".cursor",
    ".codeium",
    "venv",
    "env",
    ".env",
    ".env.local",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "Thumbs.db",
    "excel",
    "*.xlsx",
    "*.xls",
    "*.csv",
    "*.log",
    "Downloads",
    "downloads",
    "backup_*.py",
    "*.bak",
    "*.backup",
    "requests_test_url.py",
}

def should_exclude(path, name):
    """Check if a file/folder should be excluded."""
    # Check exact name match
    if name in EXCLUDE:
        return True

    # Check pattern match
    for pattern in EXCLUDE:
        if pattern.startswith("*"):
            # Pattern like *.pyc
            if name.endswith(pattern[1:]):
                return True
        elif "*" in pattern:
            # Pattern like backup_*.py
            import fnmatch
            if fnmatch.fnmatch(name, pattern):
                return True

    return False

def copy_project():
    """Copy project to git directory, excluding sensitive files."""
    print(f"Copying from {SOURCE_DIR} to {DEST_DIR}")
    print(f"Excluding: {', '.join(sorted(EXCLUDE))}")
    print()

    # Create destination directory if it doesn't exist
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    # Copy files
    files_copied = 0
    files_skipped = 0
    dirs_created = 0

    for root, dirs, files in os.walk(SOURCE_DIR):
        # Get relative path
        rel_path = Path(root).relative_to(SOURCE_DIR)

        # Skip excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(root, d)]

        # Create destination directory
        dest_root = DEST_DIR / rel_path
        if not dest_root.exists():
            dest_root.mkdir(parents=True, exist_ok=True)
            dirs_created += 1

        # Copy files
        for file in files:
            if should_exclude(root, file):
                files_skipped += 1
                continue

            src_file = Path(root) / file
            dest_file = dest_root / file

            shutil.copy2(src_file, dest_file)
            files_copied += 1

    print(f"✅ Copy complete!")
    print(f"   Files copied: {files_copied}")
    print(f"   Files skipped: {files_skipped}")
    print(f"   Directories created: {dirs_created}")
    print(f"\n📁 Destination: {DEST_DIR}")

if __name__ == "__main__":
    copy_project()
