#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Simple Working Tests
Description: Minimal working tests that focus on core functionality.
             These tests are designed to work without any encoding issues.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 15/03/2026
Version: 1.0.0
Python Version: 3.8+
License: [boazusa@hotmail.com]
===============================================================================
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from best_results_3plus_or_realtiming_race import best_race_results_per_participant
except ImportError as e:
    print(f"Warning: Could not import best_race_results_per_participant: {e}")
    print(f"Available files in project root: {list(Path('.').glob('*.py'))}")
    sys.exit(1)


class TestRaceAnalyzerBasics:
    """Test basic race analyzer functionality that works reliably."""

    @pytest.mark.unit
    def test_init_with_url(self):
        """Test initialization with URL."""
        url = "https://test.com"
        analyzer = best_race_results_per_participant(url)

        assert analyzer.url == url
        assert analyzer.race_name is None
        assert analyzer.excel_path is None

    @pytest.mark.unit
    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        url = "https://test.com"
        race_name = "Test Race"
        excel_path = "test.xlsx"

        analyzer = best_race_results_per_participant(url, race_name, excel_path)

        assert analyzer.url == url
        assert analyzer.race_name == race_name
        assert analyzer.excel_path == excel_path

    @pytest.mark.unit
    def test_url_normalization(self):
        """Test URL normalization."""
        test_cases = [
            ("https://example.com", "https://example.com"),
            ("view-source:https://example.com", "https://example.com"),
            ("http://example.com", "http://example.com"),
        ]

        for input_url, expected_url in test_cases:
            analyzer = best_race_results_per_participant(input_url)
            assert analyzer.url == expected_url


class TestNormalizationFunctions:
    """Test data normalization functions."""

    @pytest.mark.unit
    def test_normalize_year_numbers(self):
        """Test year normalization with numeric inputs."""
        assert best_race_results_per_participant.normalize_year(1980) == 1980
        assert best_race_results_per_participant.normalize_year(1980.0) == 1980
        assert best_race_results_per_participant.normalize_year(2025) == 2025

    @pytest.mark.unit
    def test_normalize_year_strings(self):
        """Test year normalization with string inputs."""
        assert best_race_results_per_participant.normalize_year("1980") == 1980
        assert best_race_results_per_participant.normalize_year("2025") == 2025

    @pytest.mark.unit
    def test_normalize_year_edge_cases(self):
        """Test year normalization edge cases."""
        assert best_race_results_per_participant.normalize_year(None) is None
        assert best_race_results_per_participant.normalize_year("") is None
        assert best_race_results_per_participant.normalize_year("invalid") is None
        assert best_race_results_per_participant.normalize_year("abcd") is None

    @pytest.mark.unit
    def test_normalize_distance_basic(self):
        """Test distance normalization with basic inputs."""
        # Test numeric inputs
        assert best_race_results_per_participant.normalize_distance("9800") == "10K"
        assert best_race_results_per_participant.normalize_distance("10000") == "10K"
        assert best_race_results_per_participant.normalize_distance("21097") == "21K"
        assert best_race_results_per_participant.normalize_distance("42195") == "42K"

        # Test None and empty
        assert pd.isna(best_race_results_per_participant.normalize_distance(None))
        assert pd.isna(best_race_results_per_participant.normalize_distance(""))
        assert pd.isna(best_race_results_per_participant.normalize_distance("unknown"))

    @pytest.mark.unit
    def test_choose_best_time_string_basic(self):
        """Test best time string selection."""
        # Test personal best preferred - using correct Hebrew column names
        row1 = pd.Series({"זמן אישי": "00:40:00", "תוצאה": "00:41:00"})
        result1 = best_race_results_per_participant.choose_best_time_string(row1)
        assert result1 == "00:40:00"

        # Test fallback to result when personal is zero
        row2 = pd.Series({"זמן אישי": "00:00:00", "תוצאה": "00:41:00"})
        result2 = best_race_results_per_participant.choose_best_time_string(row2)
        assert result2 == "00:41:00"

        # Test empty when both are zero
        row3 = pd.Series({"זמן אישי": "00:00:00", "תוצאה": "00:00:00"})
        result3 = best_race_results_per_participant.choose_best_time_string(row3)
        assert result3 == ""

        # Test empty series
        row4 = pd.Series({})
        result4 = best_race_results_per_participant.choose_best_time_string(row4)
        assert result4 == ""


class TestBasicFunctionality:
    """Test basic functionality without complex dependencies."""

    @pytest.mark.unit
    def test_excel_directory_creation(self):
        """Test that excel directory is created."""
        analyzer = best_race_results_per_participant("https://test.com")

        # Should create excel directory if it doesn't exist
        import os

        assert os.path.exists("excel")

    @pytest.mark.unit
    def test_class_instantiation(self):
        """Test that class can be instantiated."""
        # This basic test ensures the class loads properly
        analyzer = best_race_results_per_participant("https://test.com")
        assert analyzer is not None
        assert hasattr(analyzer, "url")
        assert hasattr(analyzer, "scrape_participants_table")
        assert hasattr(analyzer, "get_filtered_names")
        assert hasattr(analyzer, "normalize_year")
        assert hasattr(analyzer, "normalize_distance")
        assert hasattr(analyzer, "choose_best_time_string")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
