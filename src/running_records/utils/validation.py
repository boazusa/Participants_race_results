"""
===============================================================================
Project: Running Records Analysis
Module: Data Validation Utilities
Description: Validation functions for race data integrity.
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
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from ..exceptions import DataValidationError, InvalidYearError, InvalidDistanceError, InvalidTimeError
from .normalization import normalize_year, normalize_distance, normalize_gender, normalize_time


def validate_participant_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate participant data and return validation errors.
    
    Args:
        data: Dictionary containing participant data
        
    Returns:
        Dictionary of field names to list of error messages
        
    Examples:
        >>> data = {"first_name": "John", "birth_year": 1980, "gender": "male"}
        >>> validate_participant_data(data)
        {}
    """
    errors = {}
    
    # Validate first name
    first_name = data.get("first_name", "")
    if not first_name or str(first_name).strip() == "":
        errors.setdefault("first_name", []).append("First name is required")
    elif len(str(first_name).strip()) < 2:
        errors.setdefault("first_name", []).append("First name must be at least 2 characters")
    
    # Validate last name
    last_name = data.get("last_name", "")
    if not last_name or str(last_name).strip() == "":
        errors.setdefault("last_name", []).append("Last name is required")
    elif len(str(last_name).strip()) < 2:
        errors.setdefault("last_name", []).append("Last name must be at least 2 characters")
    
    # Validate birth year
    birth_year = data.get("birth_year")
    if birth_year is None or birth_year == "":
        errors.setdefault("birth_year", []).append("Birth year is required")
    else:
        normalized_year = normalize_year(birth_year)
        if normalized_year is None:
            errors.setdefault("birth_year", []).append("Invalid birth year format")
        elif normalized_year < 1900 or normalized_year > datetime.now().year:
            errors.setdefault("birth_year", []).append("Birth year out of valid range (1900-current year)")
    
    # Validate gender
    gender = data.get("gender")
    if gender is None or gender == "":
        errors.setdefault("gender", []).append("Gender is required")
    else:
        normalized_gender = normalize_gender(gender)
        if normalized_gender is None:
            errors.setdefault("gender", []).append("Invalid gender format")
    
    # Validate race category
    race_category = data.get("race_category", "")
    if not race_category or str(race_category).strip() == "":
        errors.setdefault("race_category", []).append("Race category is required")
    else:
        normalized_distance = normalize_distance(race_category)
        if pd.isna(normalized_distance):
            errors.setdefault("race_category", []).append("Invalid race category format")
    
    return errors


def validate_race_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate race data and return validation errors.
    
    Args:
        data: Dictionary containing race data
        
    Returns:
        Dictionary of field names to list of error messages
    """
    errors = {}
    
    # Validate race name
    race_name = data.get("name", "")
    if not race_name or str(race_name).strip() == "":
        errors.setdefault("name", []).append("Race name is required")
    
    # Validate race date
    race_date = data.get("date")
    if race_date is None or race_date == "":
        errors.setdefault("date", []).append("Race date is required")
    else:
        try:
            if isinstance(race_date, str):
                # Try to parse common date formats
                from datetime import datetime
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"]:
                    try:
                        datetime.strptime(race_date, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    errors.setdefault("date", []).append("Invalid date format")
        except Exception:
            errors.setdefault("date", []).append("Invalid date format")
    
    # Validate location
    location = data.get("location", "")
    if not location or str(location).strip() == "":
        errors.setdefault("location", []).append("Location is required")
    
    return errors


def validate_race_result_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate race result data and return validation errors.
    
    Args:
        data: Dictionary containing race result data
        
    Returns:
        Dictionary of field names to list of error messages
    """
    errors = {}
    
    # Validate participant name
    participant_name = data.get("participant_name", "")
    if not participant_name or str(participant_name).strip() == "":
        errors.setdefault("participant_name", []).append("Participant name is required")
    
    # Validate race time
    race_time = data.get("race_time", "")
    if not race_time or str(race_time).strip() == "":
        errors.setdefault("race_time", []).append("Race time is required")
    else:
        normalized_time = normalize_time(race_time)
        if normalized_time is None:
            errors.setdefault("race_time", []).append("Invalid time format (expected HH:MM:SS)")
    
    # Validate position
    position = data.get("position")
    if position is not None and position != "":
        try:
            pos_int = int(position)
            if pos_int < 1:
                errors.setdefault("position", []).append("Position must be positive")
        except (ValueError, TypeError):
            errors.setdefault("position", []).append("Position must be a valid number")
    
    return errors


def validate_dataframe_structure(df: pd.DataFrame, required_columns: List[str]) -> List[str]:
    """
    Validate DataFrame structure and return error messages.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if df.empty:
        errors.append("DataFrame is empty")
        return errors
    
    # Check required columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Check for completely empty columns
    empty_columns = [col for col in df.columns if df[col].isna().all()]
    if empty_columns:
        errors.append(f"Completely empty columns: {', '.join(empty_columns)}")
    
    # Check for duplicate rows
    if df.duplicated().any():
        duplicate_count = df.duplicated().sum()
        errors.append(f"Found {duplicate_count} duplicate rows")
    
    return errors


def validate_url(url: str) -> List[str]:
    """
    Validate URL format and accessibility.
    
    Args:
        url: URL to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if not url or str(url).strip() == "":
        errors.append("URL is required")
        return errors
    
    url_str = str(url).strip()
    
    # Basic URL format validation
    if not (url_str.startswith("http://") or url_str.startswith("https://")):
        errors.append("URL must start with http:// or https://")
    
    # Check for valid domain
    if "." not in url_str.replace("http://", "").replace("https://", "").split("/")[0]:
        errors.append("URL must contain a valid domain")
    
    return errors


def validate_age_range(min_age: int, max_age: int) -> List[str]:
    """
    Validate age range parameters.
    
    Args:
        min_age: Minimum age
        max_age: Maximum age
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if min_age < 0:
        errors.append("Minimum age cannot be negative")
    
    if max_age < 0:
        errors.append("Maximum age cannot be negative")
    
    if min_age > max_age:
        errors.append("Minimum age cannot be greater than maximum age")
    
    if max_age > 120:
        errors.append("Maximum age seems unrealistic (>120)")
    
    return errors


def validate_filter_parameters(params: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate filtering parameters.
    
    Args:
        params: Dictionary of filter parameters
        
    Returns:
        Dictionary of parameter names to list of error messages
    """
    errors = {}
    
    # Validate age range
    min_age = params.get("min_age")
    max_age = params.get("max_age")
    
    if min_age is not None and max_age is not None:
        age_errors = validate_age_range(min_age, max_age)
        if age_errors:
            errors["age_range"] = age_errors
    
    # Validate gender
    gender = params.get("gender")
    if gender is not None and gender != "":
        normalized_gender = normalize_gender(gender)
        if normalized_gender is None:
            errors.setdefault("gender", []).append("Invalid gender value")
    
    # Validate race keyword
    race_keyword = params.get("race_keyword")
    if race_keyword is not None and race_keyword != "":
        if not isinstance(race_keyword, str) or len(str(race_keyword).strip()) < 1:
            errors.setdefault("race_keyword", []).append("Race keyword must be a non-empty string")
    
    return errors


def is_valid_data_batch(data_list: List[Dict[str, Any]], validator_func) -> Dict[str, Any]:
    """
    Validate a batch of data records.
    
    Args:
        data_list: List of data dictionaries
        validator_func: Function to validate individual records
        
    Returns:
        Dictionary with validation results
    """
    results = {
        "valid_count": 0,
        "invalid_count": 0,
        "errors": {},
        "valid_indices": [],
        "invalid_indices": []
    }
    
    for i, data in enumerate(data_list):
        errors = validator_func(data)
        
        if not errors:
            results["valid_count"] += 1
            results["valid_indices"].append(i)
        else:
            results["invalid_count"] += 1
            results["invalid_indices"].append(i)
            results["errors"][i] = errors
    
    return results
