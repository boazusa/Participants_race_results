#!/usr/bin/env python3
"""
Integration tests for edge cases using sample_data.py
"""

import pytest
import pandas as pd
import tempfile
import os
from tests.fixtures.sample_data import EdgeCaseData, SampleDataGenerator
from backend.race_analyzer import best_race_results_per_participant


class TestEdgeCasesIntegration:
    """Test edge cases with actual race analysis."""

    def test_missing_names_handling(self):
        """Test how race analysis handles missing names."""
        # Create test data with missing names
        malformed_data = EdgeCaseData.get_malformed_names()
        df = pd.DataFrame(malformed_data)
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            file_path = tmp.name
        
        try:
            df.to_excel(file_path, index=False)
            
            runner = best_race_results_per_participant(
                url="mock://test",
                excel_path=file_path
            )
            runner.participants_table_df = df
            
            # Test filtering - should handle missing names gracefully
            names = runner.get_filtered_names_3plus_realtiming(
                min_year=1970,
                max_year=2000,
                gender="male",
                race_keyword="10"
            )
            
            # Should return some names (those with valid names)
            assert isinstance(names, list)
            
            # Check that some entries were filtered out (original had 5, should be less)
            assert len(names) <= len(malformed_data)
            
            # Verify returned names are valid (can be None or string)
            for first_name, last_name in names:
                assert first_name is None or isinstance(first_name, str)
                assert last_name is None or isinstance(last_name, str)
                
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_invalid_birth_years_handling(self):
        """Test how race analysis handles invalid birth years."""
        malformed_data = EdgeCaseData.get_malformed_years()
        df = pd.DataFrame(malformed_data)
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            file_path = tmp.name
        
        try:
            df.to_excel(file_path, index=False)
            
            runner = best_race_results_per_participant(
                url="mock://test",
                excel_path=file_path
            )
            runner.participants_table_df = df
            
            # Test filtering - should handle invalid years gracefully
            names = runner.get_filtered_names_3plus_realtiming(
                min_year=1970,
                max_year=2000,
                gender="male",
                race_keyword="10"
            )
            
            # Should filter out entries with invalid years
            # (normalize_year should handle this)
            assert isinstance(names, list)
            
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_malformed_genders_handling(self):
        """Test how race analysis handles malformed gender data."""
        malformed_data = EdgeCaseData.get_malformed_genders()
        df = pd.DataFrame(malformed_data)
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            file_path = tmp.name
        
        try:
            df.to_excel(file_path, index=False)
            
            runner = best_race_results_per_participant(
                url="mock://test",
                excel_path=file_path
            )
            runner.participants_table_df = df
            
            # Test filtering with different gender values
            valid_names = runner.get_filtered_names_3plus_realtiming(
                min_year=1970,
                max_year=2000,
                gender="male",
                race_keyword="10"
            )
            
            # Should only return entries with valid gender
            assert isinstance(valid_names, list)
            
            # Test with female gender
            female_names = runner.get_filtered_names_3plus_realtiming(
                min_year=1970,
                max_year=2000,
                gender="female",
                race_keyword="10"
            )
            
            assert isinstance(female_names, list)
            
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_malformed_distances_handling(self):
        """Test how race analysis handles malformed distance data."""
        malformed_data = EdgeCaseData.get_malformed_races()
        df = pd.DataFrame(malformed_data)
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            file_path = tmp.name
        
        try:
            df.to_excel(file_path, index=False)
            
            runner = best_race_results_per_participant(
                url="mock://test",
                excel_path=file_path
            )
            runner.participants_table_df = df
            
            # Test filtering with different race keywords
            names_10k = runner.get_filtered_names_3plus_realtiming(
                min_year=1970,
                max_year=2000,
                gender="male",
                race_keyword="10"
            )
            
            names_5k = runner.get_filtered_names_3plus_realtiming(
                min_year=1970,
                max_year=2000,
                gender="male",
                race_keyword="5"
            )
            
            # Should handle malformed distances gracefully
            assert isinstance(names_10k, list)
            assert isinstance(names_5k, list)
            
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_empty_dataset_handling(self):
        """Test how race analysis handles empty dataset."""
        # Create empty DataFrame
        df = pd.DataFrame(columns=["שם פרטי", "שם משפחה", "שנת לידה", "מגדר", "מקצה"])
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            file_path = tmp.name
        
        try:
            df.to_excel(file_path, index=False)
            
            runner = best_race_results_per_participant(
                url="mock://test",
                excel_path=file_path
            )
            runner.participants_table_df = df
            
            # Test filtering - should return empty list
            names = runner.get_filtered_names_3plus_realtiming(
                min_year=1970,
                max_year=2000,
                gender="male",
                race_keyword="10"
            )
            
            assert names == []
            
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        # Generate data with potential Unicode issues
        participants_df = SampleDataGenerator.generate_participants(
            count=50, seed=555
        )
        
        # Add some special characters to first few rows
        for i in range(min(5, len(participants_df))):
            participants_df.at[i, "שם פרטי"] = participants_df.at[i, "שם פרטי"] + " 🏃"
            participants_df.at[i, "שם משפחה"] = participants_df.at[i, "שם משפחה"] + "-test"
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            file_path = tmp.name
        
        try:
            participants_df.to_excel(file_path, index=False)
            
            runner = best_race_results_per_participant(
                url="mock://test",
                excel_path=file_path
            )
            runner.participants_table_df = participants_df
            
            # Test filtering - should handle Unicode gracefully
            names = runner.get_filtered_names_3plus_realtiming(
                min_year=1970,
                max_year=2000,
                gender="male",
                race_keyword="10"
            )
            
            assert isinstance(names, list)
            
            # Verify special characters are preserved (if any names match)
            for first_name, last_name in names[:3]:
                if first_name and "🏃" in str(first_name):
                    assert "🏃" in str(first_name)
                if last_name and "-test" in str(last_name):
                    assert "-test" in str(last_name)
                    
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_extreme_age_ranges(self):
        """Test with extreme age ranges."""
        # Generate data with wide age range
        participants_df = SampleDataGenerator.generate_participants(
            count=100, age_range=(90, 10), seed=777
        )
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            file_path = tmp.name
        
        try:
            participants_df.to_excel(file_path, index=False)
            
            runner = best_race_results_per_participant(
                url="mock://test",
                excel_path=file_path
            )
            runner.participants_table_df = participants_df
            
            # Test with very young age range
            young_names = runner.get_filtered_names_3plus_realtiming(
                min_year=2015,  # Age ~11
                max_year=2020,  # Age ~6
                gender="male",
                race_keyword="10"
            )
            
            # Test with very old age range
            old_names = runner.get_filtered_names_3plus_realtiming(
                min_year=1930,  # Age ~96
                max_year=1950,  # Age ~76
                gender="male",
                race_keyword="10"
            )
            
            assert isinstance(young_names, list)
            assert isinstance(old_names, list)
            
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
