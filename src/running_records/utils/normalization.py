"""
===============================================================================
Project: Running Records Analysis
Module: Data Normalization Utilities
Description: Functions for normalizing and standardizing race data.
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
import re
from datetime import datetime
from typing import Optional, Union
from ..exceptions import InvalidYearError, InvalidDistanceError


def normalize_year(year_input: Union[str, int, float, None]) -> Optional[int]:
    """
    Normalize birth year to integer format.
    
    Args:
        year_input: Year in various formats (string, int, float, or None)
        
    Returns:
        Normalized year as integer or None if invalid
        
    Examples:
        >>> normalize_year(1980)
        1980
        >>> normalize_year("1980")
        1980
        >>> normalize_year("15/10/1980")
        1980
        >>> normalize_year(None)
        None
    """
    if pd.isna(year_input) or year_input is None or year_input == "":
        return None
    
    # Handle numeric inputs
    if isinstance(year_input, (int, float)):
        year = int(year_input)
        if 1900 <= year <= datetime.now().year:
            return year
        return None
    
    # Handle string inputs
    if isinstance(year_input, str):
        year_str = year_input.strip()
        
        # Handle date format strings (DD/MM/YYYY or MM/DD/YYYY)
        if "/" in year_str:
            parts = year_str.split("/")
            try:
                if len(parts) >= 3:
                    # Assume format DD/MM/YYYY or MM/DD/YYYY
                    year = int(parts[2])
                elif len(parts) == 2:
                    # Format MM/YYYY or YYYY/MM
                    year = int(parts[1])
                elif len(parts) == 1:
                    year = int(parts[0])
                else:
                    return None
                    
                if 1900 <= year <= datetime.now().year:
                    return year
                    
            except (ValueError, IndexError):
                return None
        
        # Handle pure year strings
        try:
            year = int(year_str)
            if 1900 <= year <= datetime.now().year:
                return year
        except ValueError:
            pass
    
    return None


def normalize_distance(distance_input: Union[str, int, float, None]) -> Optional[str]:
    """
    Normalize distance string to standard format (5K, 10K, 15K, 21K, 42K).
    
    Args:
        distance_input: Distance in various formats
        
    Returns:
        Normalized distance string or None if unrecognized
        
    Examples:
        >>> normalize_distance('10 ק"מ')
        '10K'
        >>> normalize_distance("9800")
        '10K'
        >>> normalize_distance("חצי מרתון")
        '21K'
        >>> normalize_distance(None)
        None
    """
    if pd.isna(distance_input) or distance_input is None or distance_input == "":
        return np.nan
    
    distance_str = str(distance_input).strip().lower()
    
    # 10K variants
    if any(x in distance_str for x in [
        '10 ק"מ', '10ק"מ', "10000", "9800", "10 km", "10 קמ"
    ]):
        return "10K"
    
    # 21K variants (half marathon)
    if any(x in distance_str for x in [
        '21 ק"מ', '21ק"מ', "21097", "21000", "21k", "חצי מרתון", 
        "חצי מרתון תחרותי", "חצי-מרתון", "חצי_מרתון"
    ]):
        return "21K"
    
    # 42K variants (marathon)
    if any(x in distance_str for x in [
        '42 ק"מ', '42ק"מ', "42195", "42k", "מרתון", "מרתון תחרותי", '42.195 ק"מ'
    ]):
        return "42K"
    
    # 15K variants
    if any(x in distance_str for x in [
        '15 ק"מ', '15ק"מ', "15000", "15 km", "15 קמ"
    ]):
        return "15K"
    
    # 5K variants
    if any(x in distance_str for x in [
        '5 ק"מ', '5ק"מ', "5000", "5 km", "5 קמ"
    ]):
        return "5K"
    
    # Try to extract numeric distance (in meters)
    numeric_match = re.search(r'\d+', distance_str)
    if numeric_match:
        distance_meters = int(numeric_match.group())
        
        # Map common distances
        if 4800 <= distance_meters <= 5200:  # ~5K
            return "5K"
        elif 9800 <= distance_meters <= 10200:  # ~10K
            return "10K"
        elif 14800 <= distance_meters <= 15200:  # ~15K
            return "15K"
        elif 20800 <= distance_meters <= 21200:  # ~21K
            return "21K"
        elif 42100 <= distance_meters <= 42300:  # ~42K
            return "42K"
    
    return np.nan


def normalize_gender(gender_input: Union[str, None]) -> Optional[str]:
    """
    Normalize gender input to standard format.
    
    Args:
        gender_input: Gender in various formats
        
    Returns:
        Normalized gender ('male', 'female') or None
    """
    if pd.isna(gender_input) or gender_input is None or gender_input == "":
        return None
    
    gender_str = str(gender_input).strip().lower()
    
    # Male variants
    if gender_str in ['ז', 'זכר', 'male', 'm', 'man']:
        return 'male'
    
    # Female variants
    if gender_str in ['נ', 'נקבה', 'female', 'f', 'woman']:
        return 'female'
    
    return None


def normalize_time(time_input: Union[str, None]) -> Optional[str]:
    """
    Normalize time string to HH:MM:SS format.
    
    Args:
        time_input: Time string in various formats
        
    Returns:
        Normalized time string or None if invalid
    """
    if pd.isna(time_input) or time_input is None or time_input == "":
        return None
    
    time_str = str(time_input).strip()
    
    # Already in correct format
    if re.match(r'^\d{1,2}:\d{2}:\d{2}$', time_str):
        return time_str
    
    # Handle MM:SS format (add hours)
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        return f"00:{time_str}"
    
    # Handle invalid formats
    return None


def normalize_name(name_input: Union[str, None]) -> Optional[str]:
    """
    Normalize name by trimming whitespace and capitalizing properly.
    
    Args:
        name_input: Name string
        
    Returns:
        Normalized name or None if empty
    """
    if pd.isna(name_input) or name_input is None:
        return None
    
    name_str = str(name_input).strip()
    
    if not name_str or name_str.lower() in ['nan', 'none', '']:
        return None
    
    # Clean up extra whitespace
    name_str = ' '.join(name_str.split())
    
    return name_str if name_str else None


def normalize_team(team_input: Union[str, None]) -> Optional[str]:
    """
    Normalize team name.
    
    Args:
        team_input: Team name string
        
    Returns:
        Normalized team name or None if empty
    """
    return normalize_name(team_input)
