"""
===============================================================================
Project: Running Records Analysis
Module: File Utilities
Description: File system utility functions for the running records package.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
===============================================================================
"""

import os
import re
from pathlib import Path
from typing import Union, Optional
from datetime import datetime


def ensure_directory(directory_path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        Path object for the directory
        
    Examples:
        >>> ensure_directory("data/output")
        PosixPath('data/output')
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Create a safe filename by removing/replacing problematic characters.
    
    Args:
        filename: Original filename
        max_length: Maximum allowed length
        
    Returns:
        Safe filename
        
    Examples:
        >>> safe_filename("race/2024/10K.xlsx")
        'race_2024_10K.xlsx'
    """
    if not filename:
        return "unnamed"
    
    # Replace problematic characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    safe_name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', safe_name)
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed"
    
    # Truncate if too long
    if len(safe_name) > max_length:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:max_length - len(ext)] + ext
    
    return safe_name


def generate_excel_filename(
    race_name: str,
    category: str,
    age_range: str,
    timestamp: Optional[datetime] = None
) -> str:
    """
    Generate standardized Excel filename.
    
    Args:
        race_name: Name of the race
        category: Race category (e.g., "10K")
        age_range: Age range (e.g., "40-49")
        timestamp: Optional timestamp (defaults to current time)
        
    Returns:
        Generated filename
        
    Examples:
        >>> generate_excel_filename("מרוץ תל אביב", "10K", "40-49")
        '2024_04_03_14_30_00_מרוץ_תל_אביב_best_results_10K_40-49.xlsx'
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Format timestamp
    timestamp_str = timestamp.strftime("%Y_%m_%d_%H_%M_%S")
    
    # Clean race name
    clean_race_name = safe_filename(race_name)
    
    # Build filename
    filename = f"{timestamp_str}_{clean_race_name}_best_results_{category}_{age_range}.xlsx"
    
    return safe_filename(filename)


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    path = Path(file_path)
    return path.stat().st_size if path.exists() else 0


def file_exists(file_path: Union[str, Path]) -> bool:
    """
    Check if file exists and is not empty.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file exists and is not empty
    """
    path = Path(file_path)
    return path.exists() and path.stat().st_size > 0


def get_unique_filename(file_path: Union[str, Path]) -> Path:
    """
    Get a unique filename by adding number suffix if file exists.
    
    Args:
        file_path: Desired file path
        
    Returns:
        Unique file path
        
    Examples:
        >>> get_unique_filename("data.xlsx")
        PosixPath('data_1.xlsx')  # if data.xlsx already exists
    """
    path = Path(file_path)
    
    if not path.exists():
        return path
    
    counter = 1
    while True:
        stem = path.stem
        suffix = path.suffix
        new_path = path.parent / f"{stem}_{counter}{suffix}"
        
        if not new_path.exists():
            return new_path
        
        counter += 1


def cleanup_old_files(directory: Union[str, Path], pattern: str, max_files: int = 10) -> int:
    """
    Clean up old files in directory, keeping only the most recent ones.
    
    Args:
        directory: Directory to clean
        pattern: File pattern to match (e.g., "*.xlsx")
        max_files: Maximum number of files to keep
        
    Returns:
        Number of files deleted
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return 0
    
    # Get files matching pattern
    files = list(dir_path.glob(pattern))
    
    if len(files) <= max_files:
        return 0
    
    # Sort by modification time (newest first)
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # Delete oldest files
    files_to_delete = files[max_files:]
    deleted_count = 0
    
    for file_path in files_to_delete:
        try:
            file_path.unlink()
            deleted_count += 1
        except OSError:
            pass  # Ignore files that can't be deleted
    
    return deleted_count


def backup_file(file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Create a backup of a file.
    
    Args:
        file_path: File to backup
        backup_dir: Directory for backup (defaults to same directory)
        
    Returns:
        Path to backup file
    """
    source_path = Path(file_path)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")
    
    if backup_dir is None:
        backup_dir = source_path.parent
    else:
        backup_dir = Path(backup_dir)
        ensure_directory(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source_path.stem}_backup_{timestamp}{source_path.suffix}"
    backup_path = backup_dir / backup_name
    
    import shutil
    shutil.copy2(source_path, backup_path)
    
    return backup_path


def is_excel_file(file_path: Union[str, Path]) -> bool:
    """
    Check if file is an Excel file.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if Excel file
    """
    path = Path(file_path)
    return path.suffix.lower() in ['.xlsx', '.xls']


def get_temp_file_path(prefix: str = "temp", suffix: str = ".tmp") -> Path:
    """
    Get a temporary file path.
    
    Args:
        prefix: File name prefix
        suffix: File suffix
        
    Returns:
        Temporary file path
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = Path.cwd() / "temp"
    ensure_directory(temp_dir)
    
    return temp_dir / f"{prefix}_{timestamp}{suffix}"
