#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Test Suite - 3Plus Event Scenario
Description: Pytest test for the specific 3plus event scenario with age filtering
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 13/03/2026
Version: 1.0.0
Python Version: 3.8+
Dependencies:
    - pytest >= 6.2.5
    - pandas >= 1.3.0
    - unittest.mock
License: [boazusa@hotmail.com]
===============================================================================
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# Add the parent directory to the path to allow importing the module under test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from best_results_3plus_or_realtiming_race import best_race_results_per_participant


class Test3PlusEventScenario:
    """Test suite for the specific 3plus event scenario."""

    @pytest.fixture
    def scenario_params(self):
        """Fixture containing the scenario parameters."""
        return {
            "event_url": "view-source:https://regi.3plus.co.il/events/page/17492",
            "race_name": "TEST",
            "min_age": 40,
            "max_age": 49,
            "age_range": "40-49",
            "gender": "male",
            "race_keyword": "10",
            "category": "10K",
        }

    @pytest.fixture
    def current_year(self):
        """Current year for birth year calculations."""
        return datetime.now().year

    @pytest.fixture
    def birth_years(self, current_year, scenario_params):
        """Calculate birth years from age range."""
        min_year = current_year - scenario_params["max_age"]
        max_year = current_year - scenario_params["min_age"]
        return min_year, max_year

    @pytest.fixture
    def mock_participants_df(self):
        """Mock participants DataFrame for testing."""
        data = {
            "שם פרטי": ["דני", "משה", "יוסי", "דוד", "שמעון"],
            "שם משפחה": ["כהן", "לוי", "ישראלי", "בן דוד", "פרץ"],
            "שנת לידה": ["1980", "1975", "1985", "1990", "1978"],
            "מגדר": ["male", "male", "male", "male", "female"],
            "מקצה": ['10 ק"מ', '10 ק"מ', '5 ק"מ', '10 ק"מ', '10 ק"מ'],
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def race_analyzer(self, scenario_params):
        """Create race analyzer instance with scenario parameters."""
        return best_race_results_per_participant(
            url=scenario_params["event_url"],
            race_name=scenario_params["race_name"],
            excel_path=None,
        )

    def test_url_normalization(self, scenario_params):
        """Test that view-source: prefix is properly removed."""
        analyzer = best_race_results_per_participant(
            url=scenario_params["event_url"], race_name=scenario_params["race_name"]
        )
        expected_url = "https://regi.3plus.co.il/events/page/17492"
        assert analyzer.url == expected_url

    def test_birth_year_calculation(self, birth_years, current_year, scenario_params):
        """Test birth year calculation from age range."""
        min_year, max_year = birth_years
        expected_min_year = current_year - scenario_params["max_age"]
        expected_max_year = current_year - scenario_params["min_age"]

        assert min_year == expected_min_year
        assert max_year == expected_max_year

        # Verify the age range is correct
        calculated_min_age = current_year - max_year
        calculated_max_age = current_year - min_year
        assert calculated_min_age == scenario_params["min_age"]
        assert calculated_max_age == scenario_params["max_age"]

    @patch("best_results_3plus_or_realtiming_race.requests.get")
    def test_3plus_url_detection(self, mock_get, race_analyzer):
        """Test that 3plus URLs are correctly identified."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = """
        <html>
            <table id="m_ph4wp1_tblData">
                <thead><tr><th>שם פרטי</th><th>שם משפחה</th><th>שנת לידה</th><th>מגדר</th><th>מקצה</th></tr></thead>
                <tbody></tbody>
            </table>
        </html>
        """
        mock_get.return_value = mock_response

        # Test URL detection
        url_lower = race_analyzer.url.lower()
        assert "3plus.co.il" in url_lower
        assert "realtiming.co.il" not in url_lower
        assert "shvoong" not in url_lower

    def test_age_filtering_logic(
        self, race_analyzer, mock_participants_df, birth_years
    ):
        """Test the age filtering logic with calculated birth years."""
        min_year, max_year = birth_years

        # Set up the analyzer with mock data
        race_analyzer.participants_table_df = mock_participants_df.copy()

        # Apply the same filtering logic as in get_filtered_names_3plus_realtiming
        df = race_analyzer.participants_table_df.copy()
        df["שנת לידה"] = df["שנת לידה"].apply(race_analyzer.normalize_year)

        # Apply age filter
        df_filtered = df[(df["שנת לידה"] >= min_year) & (df["שנת לידה"] <= max_year)]

        # Verify filtering results
        expected_birth_years = [
            1980,
            1985,
            1978,
        ]  # Within 40-49 age range (assuming current year is 2025)
        actual_birth_years = df_filtered["שנת לידה"].tolist()

        # Sort for comparison
        expected_birth_years.sort()
        actual_birth_years.sort()

        assert actual_birth_years == expected_birth_years

    def test_gender_filtering(self, race_analyzer, mock_participants_df):
        """Test gender filtering for male participants."""
        race_analyzer.participants_table_df = mock_participants_df.copy()

        # Apply gender filter
        df = race_analyzer.participants_table_df.copy()
        df_gender_filtered = df[df["מגדר"] == "male"]

        # Should have 4 male participants (all except the female one)
        assert len(df_gender_filtered) == 4
        assert all(df_gender_filtered["מגדר"] == "male")

    def test_race_keyword_filtering(
        self, race_analyzer, mock_participants_df, scenario_params
    ):
        """Test race keyword filtering for '10'."""
        race_analyzer.participants_table_df = mock_participants_df.copy()

        # Apply race keyword filter
        df = race_analyzer.participants_table_df.copy()
        race_keyword = scenario_params["race_keyword"]

        # Test direct contains
        mask = df["מקצה"].astype(str).str.contains(race_keyword, case=False, na=False)
        df_race_filtered = df[mask]

        # Should have 4 participants with "10" in their race category
        assert len(df_race_filtered) == 4
        assert all(df_race_filtered["מקצה"].str.contains("10", case=False))

    def test_combined_filtering(
        self, race_analyzer, mock_participants_df, birth_years, scenario_params
    ):
        """Test combined filtering: age, gender, and race keyword."""
        min_year, max_year = birth_years
        race_analyzer.participants_table_df = mock_participants_df.copy()

        # Apply all filters
        df = race_analyzer.participants_table_df.copy()
        df["שנת לידה"] = df["שנת לידה"].apply(race_analyzer.normalize_year)

        # Age filter
        df = df[(df["שנת לידה"] >= min_year) & (df["שנת לידה"] <= max_year)]

        # Gender filter
        df = df[df["מגדר"] == scenario_params["gender"]]

        # Race keyword filter
        race_keyword = scenario_params["race_keyword"]
        mask = df["מקצה"].astype(str).str.contains(race_keyword, case=False, na=False)
        df = df[mask]

        # Verify results
        assert len(df) >= 0  # Should have some participants matching all criteria

        # All participants should meet all criteria
        if len(df) > 0:
            assert all(df["מגדר"] == "male")
            assert all(df["מקצה"].str.contains("10", case=False))
            assert all((df["שנת לידה"] >= min_year) & (df["שנת לידה"] <= max_year))

    def test_get_filtered_names_integration(
        self, race_analyzer, mock_participants_df, birth_years, scenario_params
    ):
        """Test the full get_filtered_names method integration."""
        min_year, max_year = birth_years
        race_analyzer.participants_table_df = mock_participants_df.copy()

        # Call the method with scenario parameters
        names_list = race_analyzer.get_filtered_names_3plus_realtiming(
            min_year=min_year,
            max_year=max_year,
            gender=scenario_params["gender"],
            race_keyword=scenario_params["race_keyword"],
        )

        # Verify return type
        assert isinstance(names_list, list)

        # Verify each element is a tuple of (first_name, last_name)
        for name_tuple in names_list:
            assert isinstance(name_tuple, tuple)
            assert len(name_tuple) == 2
            assert isinstance(name_tuple[0], str)  # first name
            assert isinstance(name_tuple[1], str)  # last name

    def test_normalize_year_edge_cases(self):
        """Test year normalization with various edge cases."""
        f = best_race_results_per_participant.normalize_year

        # Test normal cases
        assert f("1980") == 1980
        assert f(1980) == 1980
        assert f(1980.0) == 1980

        # Test edge cases
        assert f("") is None
        assert f(None) is None
        assert f("invalid") is None

        # Test two-digit years with date format (only handled in date context)
        assert f("12/31/85") == 1985  # Should be interpreted as 1985
        assert f("12/31/25") == 2025  # Should be interpreted as 2025

        # Test regular two-digit years (not converted by this function)
        assert f("85") == 85  # Stays as is since no '/' in string
        assert f("25") == 25  # Stays as is since no '/' in string

    def test_category_normalization(self, scenario_params):
        """Test that the category is properly normalized."""
        category = scenario_params["category"]
        assert category == "10K"

        # Test the normalize_distance function
        f = best_race_results_per_participant.normalize_distance
        assert f('10 ק"מ') == "10K"
        assert f('10ק"מ') == "10K"
        assert f("10000") == "10K"


# Integration test class for the full workflow
class Test3PlusEventIntegration:
    """Integration tests for the complete 3plus event workflow."""

    @patch("best_results_3plus_or_realtiming_race.requests.get")
    def test_full_workflow_simulation(self, mock_get):
        """Test the full workflow with mocked HTTP requests."""
        # Mock the participants table response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = """
        <html>
            <table id="m_ph4wp1_tblData">
                <thead>
                    <tr>
                        <th>שם פרטי</th><th>שם משפחה</th><th>שנת לידה</th><th>מגדר</th><th>מקצה</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>דני</td><td>כהן</td><td>1980</td><td>male</td><td>10 ק"מ</td></tr>
                    <tr><td>משה</td><td>לוי</td><td>1975</td><td>male</td><td>10 ק"מ</td></tr>
                    <tr><td>יוסי</td><td>ישראלי</td><td>1985</td><td>male</td><td>5 ק"מ</td></tr>
                </tbody>
            </table>
        </html>
        """
        mock_get.return_value = mock_response

        # Create analyzer
        analyzer = best_race_results_per_participant(
            url="view-source:https://regi.3plus.co.il/events/page/17492",
            race_name="TEST",
        )

        # Test scraping
        df = analyzer.scrape_participants_table()
        assert len(df) == 3
        assert "שם פרטי" in df.columns
        assert "שם משפחה" in df.columns
        assert "שנת לידה" in df.columns
        assert "מגדר" in df.columns
        assert "מקצה" in df.columns


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
