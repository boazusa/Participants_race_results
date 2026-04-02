"""
===============================================================================
Project: Running Records Analysis
Module: Time Utilities
Description: Time-related utility functions for race result processing.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
===============================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Union, Optional
from ..exceptions import InvalidTimeError


def choose_best_time_string(row: pd.Series) -> str:
    """
    Choose the best time string from personal best and race result.
    
    Prefers personal best time over race result time, unless personal best is zero.
    
    Args:
        row: Pandas Series containing 'זמן אישי' (personal best) and 'תוצאה' (result) columns
        
    Returns:
        Best time string or empty string if both are invalid
        
    Examples:
        >>> row = pd.Series({"זמן אישי": "00:40:00", "תוצאה": "00:41:00"})
        >>> choose_best_time_string(row)
        '00:40:00'
        
        >>> row = pd.Series({"זמן אישי": "00:00:00", "תוצאה": "00:41:00"})
        >>> choose_best_time_string(row)
        '00:41:00'
    """
    if not isinstance(row, pd.Series):
        return ""
    
    personal_time = row.get("זמן אישי", "")
    result_time = row.get("תוצאה", "")
    
    # Handle missing or empty values
    if pd.isna(personal_time) or personal_time in ["", "None", "NaT", "00:00:00"]:
        personal_time = ""
    
    if pd.isna(result_time) or result_time in ["", "None", "NaT", "00:00:00"]:
        result_time = ""
    
    # Prefer personal time if it's valid and not zero
    if personal_time and personal_time != "00:00:00":
        return str(personal_time)
    
    # Fall back to result time
    if result_time and result_time != "00:00:00":
        return str(result_time)
    
    return ""


def clean_timedelta(td: Union[timedelta, None]) -> str:
    """
    Convert timedelta to clean HH:MM:SS string format.
    
    Args:
        td: Timedelta object or None
        
    Returns:
        Formatted time string or empty string if None/NaT
        
    Examples:
        >>> td = timedelta(hours=1, minutes=30, seconds=45)
        >>> clean_timedelta(td)
        '01:30:45'
        
        >>> td = timedelta(minutes=45, seconds=30)
        >>> clean_timedelta(td)
        '00:45:30'
    """
    if pd.isna(td) or td is None:
        return ""
    
    if isinstance(td, timedelta):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    return ""


def parse_time_string(time_str: Union[str, None]) -> Optional[timedelta]:
    """
    Parse time string into timedelta object.
    
    Args:
        time_str: Time string in HH:MM:SS, MM:SS, or H:MM:SS format
        
    Returns:
        Timedelta object or None if invalid
        
    Examples:
        >>> parse_time_string("01:30:45")
        datetime.timedelta(seconds=5445)
        
        >>> parse_time_string("45:30")
        datetime.timedelta(seconds=2730)
    """
    if not time_str or pd.isna(time_str):
        return None
    
    time_str = str(time_str).strip()
    
    if not time_str:
        return None
    
    try:
        parts = time_str.split(':')
        
        if len(parts) == 3:
            # HH:MM:SS format
            hours, minutes, seconds = map(int, parts)
        elif len(parts) == 2:
            # MM:SS format
            hours = 0
            minutes, seconds = map(int, parts)
        else:
            return None
        
        # Validate time components
        if not (0 <= minutes < 60 and 0 <= seconds < 60 and hours >= 0):
            return None
        
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        
    except (ValueError, TypeError):
        return None


def format_timedelta(td: timedelta) -> str:
    """
    Format timedelta to human-readable string.
    
    Args:
        td: Timedelta object
        
    Returns:
        Formatted string (e.g., "1h 30m 45s")
    """
    if not isinstance(td, timedelta):
        return ""
    
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


def get_time_difference(time1: str, time2: str) -> Optional[timedelta]:
    """
    Calculate the difference between two time strings.
    
    Args:
        time1: First time string
        time2: Second time string
        
    Returns:
        Time difference as timedelta (time1 - time2) or None if invalid
    """
    td1 = parse_time_string(time1)
    td2 = parse_time_string(time2)
    
    if td1 is None or td2 is None:
        return None
    
    return td1 - td2


def is_valid_time_format(time_str: str) -> bool:
    """
    Check if time string is in valid format.
    
    Args:
        time_str: Time string to validate
        
    Returns:
        True if valid, False otherwise
    """
    return parse_time_string(time_str) is not None


def get_average_time(times: list) -> Optional[timedelta]:
    """
    Calculate average time from a list of time strings.
    
    Args:
        times: List of time strings
        
    Returns:
        Average time as timedelta or None if no valid times
    """
    valid_times = []
    
    for time_str in times:
        td = parse_time_string(time_str)
        if td is not None:
            valid_times.append(td)
    
    if not valid_times:
        return None
    
    total_seconds = sum(td.total_seconds() for td in valid_times)
    avg_seconds = total_seconds / len(valid_times)
    
    return timedelta(seconds=avg_seconds)


def get_best_time(times: list) -> Optional[timedelta]:
    """
    Get best (fastest) time from a list of time strings.
    
    Args:
        times: List of time strings
        
    Returns:
        Best time as timedelta or None if no valid times
    """
    valid_times = []
    
    for time_str in times:
        td = parse_time_string(time_str)
        if td is not None:
            valid_times.append(td)
    
    if not valid_times:
        return None
    
    return min(valid_times)


def get_worst_time(times: list) -> Optional[timedelta]:
    """
    Get worst (slowest) time from a list of time strings.
    
    Args:
        times: List of time strings
        
    Returns:
        Worst time as timedelta or None if no valid times
    """
    valid_times = []
    
    for time_str in times:
        td = parse_time_string(time_str)
        if td is not None:
            valid_times.append(td)
    
    if not valid_times:
        return None
    
    return max(valid_times)
