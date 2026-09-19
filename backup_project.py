#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup Script for RaceView Project
Copies project to versions folder with timestamp, excluding specified directories.
"""

import shutil
import os
from datetime import datetime

# Directories to exclude
EXCLUDE_DIRS = {
    'build',
    'dist',
    'excel',
    'login_info',
    'Screenshots',
    '__pycache__',
    '.pytest_cache',
    '.benchmarks',
    'tests',
    'icon',
}

# Source directory (current project)
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

# Destination base directory
DEST_BASE = r'C:\Users\USER\Documents\Python\running_records\versions'

# Generate timestamp folder name
timestamp = datetime.now().strftime('%m_%d_%Y_%H%M%S')
DEST_DIR = os.path.join(DEST_BASE, f'{timestamp}_raceview')

def should_exclude(item_name):
    """Check if item should be excluded based on name."""
    return item_name in EXCLUDE_DIRS

def copy_project():
    """Copy project excluding specified directories."""
    
    # Create destination directory
    os.makedirs(DEST_DIR, exist_ok=True)
    
    print(f"Copying project to: {DEST_DIR}")
    print(f"Excluding directories: {', '.join(EXCLUDE_DIRS)}")
    
    copied_count = 0
    excluded_count = 0
    
    # Copy all items
    for item in os.listdir(SOURCE_DIR):
        source_path = os.path.join(SOURCE_DIR, item)
        dest_path = os.path.join(DEST_DIR, item)
        
        if should_exclude(item):
            print(f"Excluding: {item}")
            excluded_count += 1
            continue
        
        if os.path.isdir(source_path):
            shutil.copytree(source_path, dest_path)
            print(f"Copied directory: {item}")
        else:
            shutil.copy2(source_path, dest_path)
            print(f"Copied file: {item}")
        
        copied_count += 1
    
    print(f"\nBackup complete!")
    print(f"Copied: {copied_count} items")
    print(f"Excluded: {excluded_count} items")
    print(f"Destination: {DEST_DIR}")

if __name__ == "__main__":
    copy_project()
