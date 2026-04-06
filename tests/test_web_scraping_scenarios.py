#!/usr/bin/env python3
"""
Web scraping scenarios using sample_data.py
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from tests.fixtures.sample_data import SampleDataGenerator, TestScenarios
from backend.race_analyzer import best_race_results_per_participant


class TestWebScrapingScenarios:
    """Test web scraping scenarios with sample data."""

    def test_3plus_scraping_scenario(self):
        """Test 3plus web scraping scenario with sample data."""
        # Generate sample data that mimics 3plus structure
        participants = SampleDataGenerator.generate_participants(
            count=100, age_range=(70, 20), gender_ratio=0.6, seed=321
        )
        
        # Convert to DataFrame with 3plus column structure
        df = pd.DataFrame(participants)
        
        # Mock the web scraping to return our sample data
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            
            # Create mock HTML with our sample data
            mock_html = self._create_mock_3plus_html(df)
            mock_response.text = mock_html
            mock_get.return_value = mock_response
            
            # Test scraping
            runner = best_race_results_per_participant(
                url="https://regi.3plus.co.il/events/page/12345",
                race_name="Test Race"
            )
            
            scraped_df = runner.scrape_3plus_participants_table()
            
            # Set the participants table for filtering
            runner.participants_table_df = scraped_df
            
            # Verify scraped data matches our sample data
            assert len(scraped_df) == len(df)
            # Check that all expected columns are present (order may differ)
            for col in df.columns:
                assert col in scraped_df.columns
            
            # Test filtering
            names = runner.get_filtered_names_3plus_realtiming(
                min_year=1950,
                max_year=2005,
                gender="male",
                race_keyword="10"
            )
            
            assert isinstance(names, list)
            # Don't require specific count since data is random

    def test_ashkelon_scraping_scenario(self):
        """Test Ashkelon web scraping scenario with sample data."""
        participants = SampleDataGenerator.generate_participants(
            count=80, age_range=(65, 25), gender_ratio=0.5, seed=654
        )
        
        df = pd.DataFrame(participants)
        
        # Mock the web scraping for Ashkelon
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            
            # Create mock HTML with Ashkelon table ID
            mock_html = self._create_mock_ashkelon_html(df)
            mock_response.text = mock_html
            mock_get.return_value = mock_response
            
            runner = best_race_results_per_participant(
                url="https://ashkelon.runisrael.org.il/iaa/category/12345",
                race_name="Ashkelon Test"
            )
            
            # Should use the 3plus method (which now handles Ashkelon)
            scraped_df = runner.scrape_participants_table()
            
            assert len(scraped_df) == len(df)
            assert "שם פרטי" in scraped_df.columns
            assert "שם משפחה" in scraped_df.columns

    def test_realtiming_scraping_scenario(self):
        """Test RealTiming web scraping scenario with sample data."""
        participants = SampleDataGenerator.generate_participants(
            count=60, age_range=(60, 30), gender_ratio=0.7, seed=987
        )
        
        df = pd.DataFrame(participants)
        
        # Mock the web scraping for RealTiming
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            
            # Create mock HTML for RealTiming
            mock_html = self._create_mock_realtiming_html(df)
            mock_response.text = mock_html
            mock_get.return_value = mock_response
            
            runner = best_race_results_per_participant(
                url="https://www.realtiming.co.il/events/1234/list",
                race_name="RealTiming Test"
            )
            
            scraped_df = runner.scrape_realtiming_participants_table()
            
            assert len(scraped_df) == len(df)

    def test_scenario_based_testing(self):
        """Test using predefined scenarios."""
        # Test basic race scenario
        basic_scenario = TestScenarios.get_3plus_scenario()
        race_config = basic_scenario
        
        # Generate participants for the scenario
        participants = SampleDataGenerator.generate_participants(
            count=50, age_range=(60, 20), gender_ratio=0.6, seed=456
        )
        
        df = pd.DataFrame(participants)
        
        # Mock web scraping
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            
            mock_html = self._create_mock_3plus_html(df)
            mock_response.text = mock_html
            mock_get.return_value = mock_response
            
            runner = best_race_results_per_participant(
                url="https://regi.3plus.co.il/events/page/12345",
                race_name=race_config.get("name", "Test Race")
            )
            
            scraped_df = runner.scrape_participants_table()
            
            # Apply scenario filters
            names = runner.get_filtered_names_3plus_realtiming(
                min_year=race_config.get("min_year", 1970),
                max_year=race_config.get("max_year", 2000),
                gender=race_config.get("gender"),
                race_keyword=race_config.get("race_keyword", "10")
            )
            
            assert isinstance(names, list)

    def test_performance_scenario(self):
        """Test performance with large dataset scenario."""
        # Generate large dataset
        participants = SampleDataGenerator.generate_participants(
            count=500, age_range=(70, 20), gender_ratio=0.5, seed=111
        )
        
        df = pd.DataFrame(participants)
        
        # Mock web scraping
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            
            mock_html = self._create_mock_3plus_html(df)
            mock_response.text = mock_html
            mock_get.return_value = mock_response
            
            import time
            start_time = time.time()
            
            runner = best_race_results_per_participant(
                url="https://regi.3plus.co.il/events/page/12345",
                race_name="Performance Test"
            )
            
            scraped_df = runner.scrape_participants_table()
            
            names = runner.get_filtered_names_3plus_realtiming(
                min_year=1980,
                max_year=1990,
                gender="male",
                race_keyword="10"
            )
            
            processing_time = time.time() - start_time
            
            assert len(scraped_df) == 500
            assert processing_time < 10.0  # Should complete within 10 seconds

    def _create_mock_3plus_html(self, df):
        """Create mock HTML for 3plus scraping."""
        html = '''
        <table id="m_ph4wp1_tblData" cellspacing="0" cellpadding="2" border="0">
            <thead>
                <tr>
        '''
        
        # Add headers based on actual DataFrame columns
        for col in df.columns:
            html += f'<th>{col}</th>'
        
        html += '''
                </tr>
            </thead>
            <tbody>
        '''
        
        for _, row in df.iterrows():
            html += '<tr>'
            for col in df.columns:
                html += f'<td>{row.get(col, "")}</td>'
            html += '</tr>'
        
        html += '''
            </tbody>
        </table>
        '''
        
        return html

    def _create_mock_ashkelon_html(self, df):
        """Create mock HTML for Ashkelon scraping."""
        html = '''
        <table id="m_ph3wp1_tblData" cellspacing="0" cellpadding="2" border="0">
            <thead>
                <tr>
                    <th>שם משפחה</th>
                    <th>שם פרטי</th>
                    <th>מגדר</th>
                    <th>שנת לידה</th>
                    <th>אגודה</th>
                    <th>מקצה</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for _, row in df.iterrows():
            html += f'''
                <tr>
                    <td>{row.get("שם משפחה", "")}</td>
                    <td>{row.get("שם פרטי", "")}</td>
                    <td>{row.get("מגדר", "")}</td>
                    <td>{row.get("שנת לידה", "")}</td>
                    <td></td>
                    <td>{row.get("מקצה", "")}</td>
                </tr>
            '''
        
        html += '''
            </tbody>
        </table>
        '''
        
        return html

    def _create_mock_realtiming_html(self, df):
        """Create mock HTML for RealTiming scraping."""
        html = '''
        <table class="table table-striped" id="participants-table">
            <thead>
                <tr>
                    <th>שם פרטי</th>
                    <th>שם משפחה</th>
                    <th>שנת לידה</th>
                    <th>מגדר</th>
                    <th>מקצה</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for _, row in df.iterrows():
            html += f'''
                <tr>
                    <td>{row.get("שם פרטי", "")}</td>
                    <td>{row.get("שם משפחה", "")}</td>
                    <td>{row.get("שנת לידה", "")}</td>
                    <td>{row.get("מגדר", "")}</td>
                    <td>{row.get("מקצה", "")}</td>
                </tr>
            '''
        
        html += '''
            </tbody>
        </table>
        '''
        
        return html
