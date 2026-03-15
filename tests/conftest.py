#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Test Configuration and Fixtures
Description: Shared fixtures, utilities, and configuration for all test modules.
             Provides common test data, mock objects, and test setup utilities.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 14/03/2026
Version: 1.0.0
Python Version: 3.8+
Dependencies:
    - pytest >= 6.2.5
    - requests-mock >= 1.8.0
    - pandas >= 1.3.0
    - numpy >= 1.21.0
License: [boazusa@hotmail.com]
===============================================================================
"""

import pytest
import pandas as pd
import numpy as np
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import project modules with error handling
try:
    from best_results_3plus_or_realtiming_race import best_race_results_per_participant
except ImportError as e:
    print(f"Warning: Could not import best_race_results_per_participant: {e}")
    best_race_results_per_participant = None

try:
    from excel_analysis import BestResultsFromExcel
except ImportError as e:
    print(f"Warning: Could not import BestResultsFromExcel: {e}")
    BestResultsFromExcel = None


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def temp_dir():
    """Temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_participants_df():
    """Sample DataFrame with race participants data."""
    data = {
        "שם פרטי": ["דני", "משה", "יוסי", "דוד", "שמעון", "שרה", "רחל", "לאה"],
        "שם משפחה": ["כהן", "לוי", "ישראלי", "בן דוד", "פרץ", "לוי", "כהן", "מזרחי"],
        "שנת לידה": ["1980", "1975", "1985", "1990", "1978", "1982", "1976", "1988"],
        "מגדר": ["male", "male", "male", "male", "male", "female", "female", "female"],
        "מקצה": [
            '10 ק"מ',
            '10 ק"מ',
            '5 ק"מ',
            '10 ק"מ',
            '21 ק"מ',
            '10 ק"מ',
            '21 ק"מ',
            '5 ק"מ',
        ],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_race_results_df():
    """Sample DataFrame with race results data."""
    data = {
        "שם פרטי": ["דני", "דני", "משה", "שרה"],
        "שם משפחה": ["כהן", "כהן", "לוי", "לוי"],
        "מקצה": ['10 ק"מ', '10 ק"מ', '10 ק"מ', '10 ק"מ'],
        "תוצאה": ["00:45:30", "00:44:15", "00:48:20", "00:52:10"],
        "זמן אישי": ["00:44:15", "00:45:30", "00:48:20", "00:52:10"],
        "מיקום כללי": ["15", "12", "25", "40"],
        "מיקום בקבוצה": ["3", "2", "5", "8"],
        "תאריך": ["01/03/2024", "15/02/2024", "01/03/2024", "01/03/2024"],
        "מקום": ["תל אביב", "ירושלים", "תל אביב", "תל אביב"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_3plus_html():
    """Sample HTML response from 3plus website."""
    return """
    <html>
        <head><title>Participants</title></head>
        <body>
            <table id="m_ph4wp1_tblData">
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
                    <tr>
                        <td>דני</td><td>כהן</td><td>1980</td><td>ז</td><td>10 ק"מ</td>
                    </tr>
                    <tr>
                        <td>משה</td><td>לוי</td><td>1975</td><td>ז</td><td>10 ק"מ</td>
                    </tr>
                    <tr>
                        <td>שרה</td><td>לוי</td><td>1982</td><td>נ</td><td>10 ק"מ</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """


@pytest.fixture
def sample_realtiming_html():
    """Sample HTML response from realtiming website."""
    return """
    <html>
        <head><title>Race Results</title></head>
        <body>
            <table>
                <thead>
                    <tr>
                        <th>מקום</th>
                        <th>שם פרטי</th>
                        <th>שם משפחה</th>
                        <th>שנת לידה</th>
                        <th>מגדר</th>
                        <th>מקצה</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td><td>דני</td><td>כהן</td><td>1980</td><td>ז</td><td>10 ק"מ</td>
                    </tr>
                    <tr>
                        <td>2</td><td>משה</td><td>לוי</td><td>1975</td><td>ז</td><td>10 ק"מ</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """


@pytest.fixture
def sample_shvoong_results_html():
    """Sample HTML response from shvoong results website."""
    return """
    <html>
        <head><title>Race Results</title></head>
        <body>
            <table>
                <thead>
                    <tr>
                        <th>שם פרטי</th>
                        <th>שם משפחה</th>
                        <th>מקצה</th>
                        <th>תוצאה</th>
                        <th>זמן אישי</th>
                        <th>מיקום כללי</th>
                        <th>תאריך</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>דני</td><td>כהן</td><td>10 ק"מ</td><td>00:44:15</td><td>00:44:15</td><td>12</td><td>15/02/2024</td>
                    </tr>
                    <tr>
                        <td>דני</td><td>כהן</td><td>10 ק"מ</td><td>00:45:30</td><td>00:44:15</td><td>15</td><td>01/03/2024</td>
                    </tr>
                    <tr>
                        <td>משה</td><td>לוי</td><td>10 ק"מ</td><td>00:48:20</td><td>00:48:20</td><td>25</td><td>01/03/2024</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """


@pytest.fixture
def race_analyzer():
    """Race analyzer instance for testing."""
    return best_race_results_per_participant(
        url="https://regi.3plus.co.il/events/page/test",
        race_name="Test Race",
        excel_path=None,
    )


@pytest.fixture
def excel_analyzer(temp_dir):
    """Excel analyzer instance for testing."""
    excel_path = temp_dir / "test_output.xlsx"
    return BestResultsFromExcel(
        excel_input_path=str(temp_dir / "test_input.xlsx"),
        race_name="Test Race",
        output_excel_path=str(excel_path),
    )


@pytest.fixture
def mock_requests_session():
    """Mock requests session for HTTP requests."""
    session = Mock()
    response = Mock()
    response.raise_for_status.return_value = None
    response.text = ""
    session.get.return_value = response
    return session


@pytest.fixture
def sample_excel_file(temp_dir, sample_participants_df):
    """Create a sample Excel file with participants data."""
    excel_path = temp_dir / "test_input.xlsx"
    sample_participants_df.to_excel(excel_path, index=False)
    return excel_path


@pytest.fixture
def current_year():
    """Current year for age calculations."""
    return datetime.now().year


@pytest.fixture
def birth_years_from_age_range(current_year):
    """Calculate birth years from common age ranges."""
    return {
        "20-29": (current_year - 29, current_year - 20),
        "30-39": (current_year - 39, current_year - 30),
        "40-49": (current_year - 49, current_year - 40),
        "50-59": (current_year - 59, current_year - 50),
    }


@pytest.fixture
def hebrew_names():
    """Sample Hebrew names for testing."""
    return {
        "first_names": [
            "דני",
            "משה",
            "יוסי",
            "דוד",
            "שמעון",
            "שרה",
            "רחל",
            "לאה",
            "רבקה",
            "מרים",
        ],
        "last_names": [
            "כהן",
            "לוי",
            "ישראלי",
            "בן דוד",
            "פרץ",
            "מזרחי",
            "גולן",
            "שמיר",
            "ברק",
            "פרץ",
        ],
    }


@pytest.fixture
def race_categories():
    """Common race categories for testing."""
    return {
        "5K": ['5 ק"מ', '5ק"מ', "5000", "5 km"],
        "10K": ['10 ק"מ', '10ק"מ', "10000", "9800", "10 km"],
        "15K": ['15 ק"מ', '15ק"מ', "15000", "15 km"],
        "21K": ['21 ק"מ', '21ק"מ', "21097", "21000", "חצי מרתון", "חצי מרתון תחרותי"],
        "42K": ['42 ק"מ', '42ק"מ', "42195", "מרתון", "מרתון תחרותי"],
    }


@pytest.fixture
def mock_flask_client():
    """Mock Flask test client."""
    from flask_app import app

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_single_person_flask_client():
    """Mock single person Flask test client."""
    from single_person_flask_app import app

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Test data generators
@pytest.fixture
def generate_participant_data():
    """Generate participant data with specified parameters."""

    def _generate(count=10, age_range=(30, 50), gender_ratio=0.7):
        """Generate specified number of participants."""
        np.random.seed(42)  # For reproducible tests

        first_names = ["דני", "משה", "יוסי", "דוד", "שמעון", "שרה", "רחל", "לאה"]
        last_names = ["כהן", "לוי", "ישראלי", "בן דוד", "פרץ", "מזרחי"]
        categories = ['10 ק"מ', '21 ק"מ', '5 ק"מ']

        data = {
            "שם פרטי": np.random.choice(first_names, count),
            "שם משפחה": np.random.choice(last_names, count),
            "שנת לידה": np.random.randint(age_range[1], age_range[0], count).astype(
                str
            ),
            "מגדר": np.random.choice(
                ["male", "female"], count, p=[gender_ratio, 1 - gender_ratio]
            ),
            "מקצה": np.random.choice(categories, count),
        }

        return pd.DataFrame(data)

    return _generate


# Performance testing fixtures
@pytest.fixture
def large_dataset():
    """Generate large dataset for performance testing."""

    def _generate(size=1000):
        """Generate dataset with specified size."""
        first_names = ["דני", "משה", "יוסי", "דוד", "שמעון", "שרה", "רחל", "לאה"] * 125
        last_names = ["כהן", "לוי", "ישראלי", "בן דוד", "פרץ", "מזרחי"] * 167
        categories = ['10 ק"מ', '21 ק"מ', '5 ק"מ', '15 ק"מ', '42 ק"מ']

        data = {
            "שם פרטי": first_names[:size],
            "שם משפחה": last_names[:size],
            "שנת לידה": np.random.randint(1970, 2005, size).astype(str),
            "מגדר": np.random.choice(["male", "female"], size),
            "מקצה": np.random.choice(categories, size),
        }

        return pd.DataFrame(data)

    return _generate


# Error scenario fixtures
@pytest.fixture
def network_error_mock():
    """Mock network error scenarios."""

    class NetworkErrorMock:
        def __init__(self):
            self.call_count = 0
            self.fail_on_call = 1
            self.error_type = "timeout"

        def get(self, url, **kwargs):
            self.call_count += 1
            if self.call_count == self.fail_on_call:
                if self.error_type == "timeout":
                    raise TimeoutError("Request timeout")
                elif self.error_type == "connection":
                    raise ConnectionError("Connection failed")
                elif self.error_type == "http_error":
                    response = Mock()
                    response.raise_for_status.side_effect = Exception("HTTP Error")
                    return response
            else:
                response = Mock()
                response.raise_for_status.return_value = None
                response.text = ""
                return response

    return NetworkErrorMock()


# Test markers configuration
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "web_scraping: Web scraping tests")
    config.addinivalue_line("markers", "flask: Flask application tests")
    config.addinivalue_line("markers", "excel: Excel file tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "external: Tests requiring external services")
    config.addinivalue_line("markers", "hebrew: Hebrew text handling tests")


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    for item in items:
        # Add slow marker to performance tests
        if "performance" in item.keywords:
            item.add_marker(pytest.mark.slow)

        # Add external marker to web scraping tests
        if "web_scraping" in item.keywords:
            item.add_marker(pytest.mark.external)
