#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Test Helper Functions
Description: Utility functions and helpers for testing the running records system.
             Provides common testing patterns, assertions, and validation functions.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 14/03/2026
Version: 1.0.0
Python Version: 3.8+
License: [boazusa@hotmail.com]
===============================================================================
"""

import pandas as pd
import numpy as np
import requests
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path


class DataFrameAssertions:
    """Custom assertions for DataFrame testing."""
    
    @staticmethod
    def assert_dataframe_structure(df, expected_columns, min_rows=0):
        """Assert DataFrame has expected structure."""
        assert isinstance(df, pd.DataFrame), f"Expected DataFrame, got {type(df)}"
        assert len(df) >= min_rows, f"Expected at least {min_rows} rows, got {len(df)}"
        
        missing_columns = set(expected_columns) - set(df.columns)
        assert not missing_columns, f"Missing columns: {missing_columns}"
        
        extra_columns = set(df.columns) - set(expected_columns)
        if extra_columns:
            print(f"Warning: Extra columns found: {extra_columns}")
    
    @staticmethod
    def assert_hebrew_text_present(df, columns):
        """Assert that Hebrew text is present in specified columns."""
        for col in columns:
            if col in df.columns:
                hebrew_found = df[col].astype(str).str.contains(r'[\u0590-\u05FF]', na=False).any()
                assert hebrew_found, f"No Hebrew text found in column '{col}'"
    
    @staticmethod
    def assert_data_types(df, expected_types):
        """Assert DataFrame columns have expected data types."""
        for col, expected_type in expected_types.items():
            if col in df.columns:
                actual_type = df[col].dtype
                if expected_type == 'hebrew_string':
                    # Check if column contains Hebrew text
                    has_hebrew = df[col].astype(str).str.contains(r'[\u0590-\u05FF]', na=False).any()
                    assert has_hebrew, f"Column '{col}' should contain Hebrew text"
                else:
                    assert actual_type == expected_type, f"Column '{col}' type mismatch: expected {expected_type}, got {actual_type}"
    
    @staticmethod
    def assert_age_range(df, birth_year_col, min_age, max_age, current_year=None):
        """Assert participants are within specified age range."""
        if current_year is None:
            current_year = datetime.now().year
        
        if birth_year_col in df.columns:
            df_copy = df.copy()
            df_copy[birth_year_col] = pd.to_numeric(df_copy[birth_year_col], errors='coerce')
            
            min_birth_year = current_year - max_age
            max_birth_year = current_year - min_age
            
            valid_ages = df_copy[
                (df_copy[birth_year_col] >= min_birth_year) & 
                (df_copy[birth_year_col] <= max_birth_year)
            ]
            
            assert len(valid_ages) > 0, "No participants within specified age range"
            
            # Check if all participants are within range (if that's expected)
            out_of_range = df_copy[
                (df_copy[birth_year_col] < min_birth_year) | 
                (df_copy[birth_year_col] > max_birth_year)
            ]
            
            if len(out_of_range) > 0:
                print(f"Warning: {len(out_of_range)} participants outside age range")
    
    @staticmethod
    def assert_gender_filter(df, gender_col, expected_gender):
        """Assert gender filtering works correctly."""
        if gender_col in df.columns:
            filtered_df = df[df[gender_col] == expected_gender]
            assert len(filtered_df) > 0, f"No participants with gender '{expected_gender}'"
            
            # Check if any other genders are present
            other_genders = df[df[gender_col] != expected_gender]
            if len(other_genders) > 0:
                print(f"Warning: {len(other_genders)} participants with different gender")


class HTTPMockHelpers:
    """Helpers for mocking HTTP requests."""
    
    @staticmethod
    def create_mock_response(status_code=200, text="", headers=None, raise_for_status=None):
        """Create a mock HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = text
        mock_response.headers = headers or {}
        
        if raise_for_status:
            mock_response.raise_for_status.side_effect = raise_for_status
        else:
            mock_response.raise_for_status.return_value = None
        
        return mock_response
    
    @staticmethod
    def mock_requests_get(url, response_data):
        """Create a mock for requests.get with specific response."""
        mock_response = HTTPMockHelpers.create_mock_response(**response_data)
        
        def get_side_effect(request_url, **kwargs):
            if request_url == url:
                return mock_response
            else:
                raise ValueError(f"Unexpected URL: {request_url}")
        
        return patch('requests.get', side_effect=get_side_effect)
    
    @staticmethod
    def mock_timeout_error(url):
        """Mock a timeout error for requests.get."""
        def timeout_side_effect(request_url, **kwargs):
            if request_url == url:
                raise requests.exceptions.Timeout("Request timeout")
            else:
                raise ValueError(f"Unexpected URL: {request_url}")
        
        return patch('requests.get', side_effect=timeout_side_effect)
    
    @staticmethod
    def mock_connection_error(url):
        """Mock a connection error for requests.get."""
        def connection_side_effect(request_url, **kwargs):
            if request_url == url:
                raise requests.exceptions.ConnectionError("Connection failed")
            else:
                raise ValueError(f"Unexpected URL: {request_url}")
        
        return patch('requests.get', side_effect=connection_side_effect)


class FileSystemHelpers:
    """Helpers for file system operations in tests."""
    
    @staticmethod
    def create_temp_excel_file(df, filename="test.xlsx"):
        """Create a temporary Excel file with given DataFrame."""
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, filename)
        
        df.to_excel(file_path, index=False, engine='openpyxl')
        return file_path, temp_dir
    
    @staticmethod
    def create_temp_csv_file(df, filename="test.csv"):
        """Create a temporary CSV file with given DataFrame."""
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, filename)
        
        df.to_csv(file_path, index=False, encoding='utf-8')
        return file_path, temp_dir
    
    @staticmethod
    def cleanup_temp_files(temp_dir):
        """Clean up temporary directory and files."""
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
    
    @staticmethod
    def assert_file_exists(file_path):
        """Assert that a file exists."""
        assert os.path.exists(file_path), f"File does not exist: {file_path}"
    
    @staticmethod
    def assert_file_not_empty(file_path):
        """Assert that a file is not empty."""
        assert os.path.exists(file_path), f"File does not exist: {file_path}"
        assert os.path.getsize(file_path) > 0, f"File is empty: {file_path}"


class PerformanceHelpers:
    """Helpers for performance testing."""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        return result, execution_time
    
    @staticmethod
    def assert_execution_time(execution_time, max_seconds):
        """Assert execution time is within acceptable limits."""
        assert execution_time <= max_seconds, f"Execution time {execution_time}s exceeds maximum {max_seconds}s"
    
    @staticmethod
    def measure_memory_usage(func, *args, **kwargs):
        """Measure memory usage of a function."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            result = func(*args, **kwargs)
            
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            return result, memory_used
        except ImportError:
            print("Warning: psutil not available, memory measurement skipped")
            return func(*args, **kwargs), 0
    
    @staticmethod
    def assert_memory_usage(memory_used_mb, max_mb):
        """Assert memory usage is within acceptable limits."""
        assert memory_used_mb <= max_mb, f"Memory usage {memory_used_mb}MB exceeds maximum {max_mb}MB"


class ValidationHelpers:
    """Helpers for data validation in tests."""
    
    @staticmethod
    def validate_hebrew_text(text):
        """Validate that text contains Hebrew characters."""
        if pd.isna(text) or text == "":
            return False
        
        return bool(re.search(r'[\u0590-\u05FF]', str(text)))
    
    @staticmethod
    def validate_race_time(time_str):
        """Validate race time format (HH:MM:SS)."""
        if pd.isna(time_str) or time_str == "":
            return False
        
        try:
            time_parts = str(time_str).split(':')
            if len(time_parts) != 3:
                return False
            
            hours, minutes, seconds = map(int, time_parts)
            return (0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_birth_year(year_str):
        """Validate birth year format."""
        if pd.isna(year_str) or year_str == "":
            return False
        
        try:
            year = int(str(year_str).strip())
            current_year = datetime.now().year
            return 1900 <= year <= current_year
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_gender(gender_str):
        """Validate gender format."""
        if pd.isna(gender_str) or gender_str == "":
            return False
        
        valid_genders = ['male', 'female', 'ז', 'נ', 'זכר', 'נקבה']
        return str(gender_str).lower() in valid_genders
    
    @staticmethod
    def validate_dataframe_quality(df, required_columns=None):
        """Validate overall DataFrame quality."""
        issues = []
        
        # Check for empty DataFrame
        if df.empty:
            issues.append("DataFrame is empty")
        
        # Check for required columns
        if required_columns:
            missing_cols = set(required_columns) - set(df.columns)
            if missing_cols:
                issues.append(f"Missing required columns: {missing_cols}")
        
        # Check for completely empty columns
        empty_cols = [col for col in df.columns if df[col].isna().all()]
        if empty_cols:
            issues.append(f"Completely empty columns: {empty_cols}")
        
        # Check for duplicate rows
        if df.duplicated().any():
            duplicate_count = df.duplicated().sum()
            issues.append(f"Found {duplicate_count} duplicate rows")
        
        return issues


class TestDataManager:
    """Manages test data setup and cleanup."""
    
    def __init__(self, temp_dir=None):
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        self.created_files = []
        self.created_dirs = []
    
    def create_excel_file(self, df, filename):
        """Create Excel file and track for cleanup."""
        file_path = os.path.join(self.temp_dir, filename)
        df.to_excel(file_path, index=False, engine='openpyxl')
        self.created_files.append(file_path)
        return file_path
    
    def create_csv_file(self, df, filename):
        """Create CSV file and track for cleanup."""
        file_path = os.path.join(self.temp_dir, filename)
        df.to_csv(file_path, index=False, encoding='utf-8')
        self.created_files.append(file_path)
        return file_path
    
    def create_directory(self, dirname):
        """Create directory and track for cleanup."""
        dir_path = os.path.join(self.temp_dir, dirname)
        os.makedirs(dir_path, exist_ok=True)
        self.created_dirs.append(dir_path)
        return dir_path
    
    def cleanup(self):
        """Clean up all created files and directories."""
        import shutil
        
        for file_path in self.created_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        
        for dir_path in self.created_dirs:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                except OSError:
                    pass
        
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except OSError:
                pass


# Context managers for common test patterns
class TempExcelFile:
    """Context manager for temporary Excel files."""
    
    def __init__(self, df, filename="test.xlsx"):
        self.df = df
        self.filename = filename
        self.file_path = None
        self.temp_dir = None
def __init__(self, df, filename="test.xlsx"):
    self.df = df
    self.filename = filename
    self.file_path = None
    self.temp_dir = None
    
def __enter__(self):
    self.file_path, self.temp_dir = FileSystemHelpers.create_temp_excel_file(self.df, self.filename)
    return self.file_path
    
def __exit__(self, exc_type, exc_val, exc_tb):
    FileSystemHelpers.cleanup_temp_files(self.temp_dir)


class MockHTTPServer:
    """Context manager for mocking HTTP server responses."""
    
def __init__(self, url, response_data):
    self.url = url
    self.response_data = response_data
    self.mock_patch = None
    
def __enter__(self):
    self.mock_patch = HTTPMockHelpers.mock_requests_get(self.url, self.response_data)
    self.mock_patch.start()
    return self.mock_patch
    
def __exit__(self, exc_type, exc_val, exc_tb):
    if self.mock_patch:
        self.mock_patch.stop()


# Utility functions for common test operations
def assert_dataframe_equals(actual, expected, check_dtype=True, check_column_order=False):
    """Assert two DataFrames are equal with helpful error messages."""
    try:
        pd.testing.assert_frame_equal(
            actual, 
            expected, 
            check_dtype=check_dtype, 
            check_like=not check_column_order
        )
    except AssertionError as e:
        print(f"DataFrame comparison failed:")
        print(f"Actual shape: {actual.shape}")
        print(f"Expected shape: {expected.shape}")
        print(f"Actual columns: {list(actual.columns)}")
        print(f"Expected columns: {list(expected.columns)}")
        raise


def create_sample_dataframe(size=10, seed=42):
    """Create a sample DataFrame for testing."""
    np.random.seed(seed)
    
    data = {
        'first_name': [f'Name{i}' for i in range(size)],
        'last_name': [f'Surname{i}' for i in range(size)],
        'birth_year': np.random.randint(1970, 2000, size),
        'gender': np.random.choice(['male', 'female'], size),
        'race': np.random.choice(['10K', '21K', '5K'], size)
    }
    
    return pd.DataFrame(data)
