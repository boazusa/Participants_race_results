#!/usr/bin/env python3
"""
Integration tests using sample_data.py generators
"""

import pytest
import pandas as pd
import tempfile
import os
from tests.fixtures.sample_data import SampleDataGenerator, TestScenarios, EdgeCaseData
from backend.race_analyzer import best_race_results_per_participant


class TestSampleDataIntegration:
    """Test the sample data generators with actual race analysis."""

    def test_sample_data_generator_basic(self):
        """Test basic sample data generation."""
        participants_df = SampleDataGenerator.generate_participants(
            count=50, age_range=(50, 30), gender_ratio=0.7, seed=42
        )
        
        assert len(participants_df) == 50
        assert "שם פרטי" in participants_df.columns
        assert "שם משפחה" in participants_df.columns
        assert "שנת לידה" in participants_df.columns
        assert "מגדר" in participants_df.columns

    def test_sample_data_generator_with_excel(self):
        """Test sample data generation with Excel file creation."""
        file_path, participants_df, results_df = SampleDataGenerator.generate_excel_data(
            file_path="test_sample.xlsx", participants_count=30, seed=123
        )
        
        try:
            assert os.path.exists(file_path)
            assert len(participants_df) == 30
            assert len(results_df) > 0
            
            # Verify data structure
            expected_columns = ["שם פרטי", "שם משפחה", "שנת לידה", "מגדר", "מקצה"]
            for col in expected_columns:
                assert col in participants_df.columns
                
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_test_scenarios_basic_race(self):
        """Test basic race scenario."""
        scenario_data = TestScenarios.get_3plus_scenario()
        
        assert "url" in scenario_data
        assert "race_name" in scenario_data
        assert "min_age" in scenario_data
        assert "max_age" in scenario_data
        
        # Verify scenario structure
        assert scenario_data["min_age"] == 40
        assert scenario_data["max_age"] == 49
        assert scenario_data["gender"] == "male"

    def test_test_scenarios_realtiming_race(self):
        """Test realtiming scenario."""
        scenario_data = TestScenarios.get_realtiming_scenario()
        
        assert "url" in scenario_data
        assert "race_name" in scenario_data
        assert scenario_data["min_age"] == 30
        assert scenario_data["max_age"] == 50
        assert scenario_data["gender"] == "female"

    def test_edge_case_data_malformed_names(self):
        """Test edge case with malformed names."""
        malformed_data = EdgeCaseData.get_malformed_names()
        
        assert len(malformed_data) > 0
        # Should have some empty/None names
        has_missing = any(
            not p.get("שם פרטי") or not p.get("שם משפחה") 
            for p in malformed_data
        )
        assert has_missing

    def test_edge_case_data_invalid_years(self):
        """Test edge case with invalid birth years."""
        malformed_data = EdgeCaseData.get_malformed_years()
        
        assert len(malformed_data) > 0
        # Should have some invalid years
        has_invalid = any(
            not str(p["שנת לידה"]).isdigit() or int(p["שנת לידה"]) < 1900
            for p in malformed_data
        )
        assert has_invalid

    def test_integration_with_race_analysis(self):
        """Test sample data integration with actual race analysis."""
        # Create temporary Excel file with sample data
        file_path, participants_df, _ = SampleDataGenerator.generate_excel_data(
            file_path="test_integration.xlsx", participants_count=20, seed=456
        )
        
        try:
            # Test with the race analysis class
            runner = best_race_results_per_participant(
                url="mock://test",  # Mock URL since we're using Excel
                excel_path=file_path
            )
            
            # Load participants from Excel
            runner.participants_table_df = participants_df
            
            # Test filtering
            names = runner.get_filtered_names_3plus_realtiming(
                min_year=1976,
                max_year=1990,
                gender="male",
                race_keyword="10"
            )
            
            assert isinstance(names, list)
            
            # Verify name format
            for first_name, last_name in names[:5]:  # Check first 5
                assert isinstance(first_name, str)
                assert isinstance(last_name, str)
                
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_large_dataset_performance(self):
        """Test performance with large dataset."""
        import time
        
        start_time = time.time()
        
        # Generate large dataset
        participants = SampleDataGenerator.generate_participants(
            count=1000, age_range=(70, 20), gender_ratio=0.5, seed=789
        )
        
        generation_time = time.time() - start_time
        
        assert len(participants) == 1000
        assert generation_time < 5.0  # Should complete within 5 seconds

    def test_data_consistency(self):
        """Test data consistency across multiple runs."""
        # Generate data with same seed
        participants1 = SampleDataGenerator.generate_participants(
            count=50, age_range=(60, 20), seed=999
        )
        participants2 = SampleDataGenerator.generate_participants(
            count=50, age_range=(60, 20), seed=999
        )
        
        # Should be identical
        assert participants1.equals(participants2)
        
        # Different seeds should produce different data
        participants3 = SampleDataGenerator.generate_participants(
            count=50, age_range=(60, 20), seed=888
        )
        assert not participants1.equals(participants3)
