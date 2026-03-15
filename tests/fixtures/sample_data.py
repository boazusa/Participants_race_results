#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Sample Test Data
Description: Sample data generators and fixtures for testing the running records system.
             Includes realistic Hebrew names, race data, and various test scenarios.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 14/03/2026
Version: 1.0.0
Python Version: 3.8+
License: [boazusa@hotmail.com]
==============================================================================="""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


class SampleDataGenerator:
    """Generate sample data for testing running records analysis."""

    # Hebrew names and data
    HEBREW_FIRST_NAMES = {
        "male": [
            "דני",
            "משה",
            "יוסי",
            "דוד",
            "שמעון",
            "אברהם",
            "יצחק",
            "יעקב",
            "יוסף",
            "אהרון",
            "אליעזר",
            "ישראל",
            "מאיר",
            "יהודה",
            "לוי",
            "בנימין",
            "שלמה",
            "שמואל",
            "נתן",
            "דוד",
        ],
        "female": [
            "שרה",
            "רחל",
            "לאה",
            "רבקה",
            "מרים",
            "דבורה",
            "אסתר",
            "יעל",
            "תמר",
            "נועה",
            "מיכל",
            "אביגיל",
            "חנה",
            "גילה",
            "עדי",
            "ליאת",
            "אורלי",
            "קרן",
            "שירה",
            "רות",
        ],
    }

    HEBREW_LAST_NAMES = [
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
        "אברהם",
        "יצחק",
        "יעקב",
        "יוסף",
        "לוי",
        "כהן",
        "שמעוני",
        "דוד",
        "שלמה",
        "שמואל",
        "מרדכי",
        "אהרוני",
        "אליעזר",
        "ישראל",
        "מאיר",
        "יהודה",
        "בנימין",
        "שלמה",
        "שמואל",
        "נתן",
    ]

    RACE_CATEGORIES = {
        "5K": ['5 ק"מ', '5ק"מ', "5000", "5 km", "5 קמ"],
        "10K": ['10 ק"מ', '10ק"מ', "10000", "9800", "10 km", "10 קמ"],
        "15K": ['15 ק"מ', '15ק"מ', "15000", "15 km", "15 קמ"],
        "21K": [
            '21 ק"מ',
            '21ק"מ',
            "21097",
            "21000",
            "חצי מרתון",
            "חצי מרתון תחרותי",
            "חצי-מרתון",
        ],
        "42K": ['42 ק"מ', '42ק"מ', "42195", "מרתון", "מרתון תחרותי", '42.195 ק"מ'],
    }

    TEAMS = [
        "מכבי תל אביב",
        "הפועל ירושלים",
        'בית"ר תל אביב',
        "מכבי חיפה",
        "הפועל תל אביב",
        "מכבי פתח תקווה",
        "הפועל פתח תקווה",
        "בני יהודה",
        "הפועל חיפה",
        "מכבי נתניה",
        "מכבי ראשון לציון",
        "הפועל ראשון לציון",
        'בית"ר ירושלים',
        "הפועל כפר סבא",
        "מכבי כפר סבא",
    ]

    LOCATIONS = [
        "תל אביב",
        "ירושלים",
        "חיפה",
        "באר שבע",
        "פתח תקווה",
        "ראשון לציון",
        "נתניה",
        "חולון",
        "בני ברק",
        "רמת גן",
        "אשדוד",
        "רחובות",
        "בת ים",
        "כפר סבא",
        "הרצליה",
        "מודיעין",
        "רעננה",
        "גבעתיים",
        "קריית אונו",
        "חדרה",
    ]

    @classmethod
    def generate_participants(
        cls, count=10, age_range=(20, 60), gender_ratio=0.6, seed=None
    ):
        """Generate participants DataFrame."""
        if seed:
            np.random.seed(seed)
            random.seed(seed)

        participants = []

        for i in range(count):
            # Choose gender
            gender = "male" if random.random() < gender_ratio else "female"

            # Choose names
            first_name = random.choice(cls.HEBREW_FIRST_NAMES[gender])
            last_name = random.choice(cls.HEBREW_LAST_NAMES)

            # Generate birth year from age range
            birth_year = random.randint(age_range[1], age_range[0])

            # Choose race category
            category = random.choice(list(cls.RACE_CATEGORIES.keys()))
            race_type = random.choice(cls.RACE_CATEGORIES[category])

            # Choose team
            team = random.choice(cls.TEAMS)

            participants.append(
                {
                    "שם פרטי": first_name,
                    "שם משפחה": last_name,
                    "שנת לידה": str(birth_year),
                    "מגדר": gender,
                    "מקצה": race_type,
                    "קבוצה": team,
                }
            )

        return pd.DataFrame(participants)

    @classmethod
    def generate_race_results(
        cls, participants_df, num_results_per_person=3, seed=None
    ):
        """Generate race results for given participants."""
        if seed:
            np.random.seed(seed)
            random.seed(seed)

        results = []

        for _, participant in participants_df.iterrows():
            first_name = participant["שם פרטי"]
            last_name = participant["שם משפחה"]

            for i in range(num_results_per_person):
                # Generate race date within last 2 years
                days_ago = random.randint(0, 730)
                race_date = datetime.now() - timedelta(days=days_ago)
                date_str = race_date.strftime("%d/%m/%Y")

                # Choose location
                location = random.choice(cls.LOCATIONS)

                # Determine race category
                original_race = participant["מקצה"]
                normalized_race = cls.normalize_distance(original_race)

                # Generate realistic race times based on category
                if normalized_race == "5K":
                    base_time = timedelta(minutes=random.randint(20, 35))
                elif normalized_race == "10K":
                    base_time = timedelta(minutes=random.randint(40, 65))
                elif normalized_race == "15K":
                    base_time = timedelta(minutes=random.randint(60, 90))
                elif normalized_race == "21K":
                    base_time = timedelta(minutes=random.randint(80, 130))
                elif normalized_race == "42K":
                    base_time = timedelta(minutes=random.randint(180, 240))
                else:
                    base_time = timedelta(minutes=45)

                # Add some variation
                variation = timedelta(seconds=random.randint(-120, 120))
                race_time = base_time + variation

                # Generate personal best (usually better than current time)
                pb_variation = timedelta(seconds=random.randint(-300, 60))
                personal_best = race_time + pb_variation

                # Ensure personal best is not worse than race time
                if personal_best > race_time:
                    personal_best = race_time

                # Generate positions
                overall_position = random.randint(1, 500)
                group_position = random.randint(1, 50)

                results.append(
                    {
                        "תאריך": date_str,
                        "מקום": location,
                        "שם פרטי": first_name,
                        "שם משפחה": last_name,
                        "מקצה": original_race,
                        "תוצאה": cls.format_time(race_time),
                        "זמן אישי": cls.format_time(personal_best),
                        "מיקום כללי": str(overall_position),
                        "מיקום בקבוצה": str(group_position),
                    }
                )

        return pd.DataFrame(results)

    @staticmethod
    def normalize_distance(distance_str):
        """Normalize distance string to standard format."""
        if pd.isna(distance_str) or str(distance_str).strip() == "":
            return np.nan

        s = str(distance_str).strip()

        if s in ['10 ק"מ', '10ק"מ', "9800", "10000", "10 קמ"]:
            return "10K"
        elif s in [
            "21097",
            '21 ק"מ',
            "21000",
            "21K",
            "21k",
            "חצי מרתון",
            "חצי מרתון תחרותי",
            "חצי-מרתון",
        ]:
            return "21K"
        elif s in ["42195", "42K", "42k", '42 ק"מ', "מרתון"]:
            return "42K"
        elif "15" in s:
            return "15K"
        elif "5" in s and "2" not in s:
            return "5K"

        return np.nan

    @staticmethod
    def format_time(timedelta_obj):
        """Format timedelta object to HH:MM:SS string."""
        total_seconds = int(timedelta_obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @classmethod
    def generate_excel_data(cls, file_path, participants_count=50, seed=None):
        """Generate Excel file with participants and results."""
        # Generate participants
        participants_df = cls.generate_participants(
            count=participants_count, age_range=(20, 65), gender_ratio=0.55, seed=seed
        )

        # Generate race results
        results_df = cls.generate_race_results(
            participants_df, num_results_per_person=3, seed=seed
        )

        # Save to Excel
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            participants_df.to_excel(writer, sheet_name="Participants", index=False)
            results_df.to_excel(writer, sheet_name="Results", index=False)

        return file_path, participants_df, results_df


class TestScenarios:
    """Predefined test scenarios for common use cases."""

    @staticmethod
    def get_3plus_scenario():
        """Get scenario for 3plus website testing."""
        return {
            "url": "view-source:https://regi.3plus.co.il/events/page/17492",
            "race_name": "TEST",
            "min_age": 40,
            "max_age": 49,
            "age_range": "40-49",
            "gender": "male",
            "race_keyword": "10",
            "category": "10K",
            "expected_participants": 3,  # Based on sample data
        }

    @staticmethod
    def get_realtiming_scenario():
        """Get scenario for realtiming website testing."""
        return {
            "url": "https://www.realtiming.co.il/events/1242/list",
            "race_name": "Beit Shemesh",
            "min_age": 30,
            "max_age": 50,
            "age_range": "30-50",
            "gender": "female",
            "race_keyword": "21",
            "category": "21K",
            "expected_participants": 2,
        }

    @staticmethod
    def get_large_dataset_scenario():
        """Get scenario for performance testing with large dataset."""
        return {
            "url": "https://regi.3plus.co.il/events/page/large",
            "race_name": "Large Race",
            "min_age": 20,
            "max_age": 60,
            "age_range": "20-60",
            "gender": None,  # All genders
            "race_keyword": "10",
            "category": "10K",
            "expected_participants": 1000,
        }

    @staticmethod
    def get_hebrew_text_scenario():
        """Get scenario for Hebrew text handling testing."""
        return {
            "url": "https://regi.3plus.co.il/events/page/hebrew",
            "race_name": "מרוץ תל אביב",
            "min_age": 25,
            "max_age": 35,
            "age_range": "25-35",
            "gender": "male",
            "race_keyword": "חצי",
            "category": "21K",
            "expected_participants": 5,
        }


class EdgeCaseData:
    """Data for edge case testing."""

    @staticmethod
    def get_malformed_names():
        """Get participants with malformed or edge case names."""
        return [
            {
                "שם פרטי": "",
                "שם משפחה": "כהן",
                "שנת לידה": "1980",
                "מגדר": "male",
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": "דני",
                "שם משפחה": "",
                "שנת לידה": "1980",
                "מגדר": "male",
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": None,
                "שם משפחה": "לוי",
                "שנת לידה": "1975",
                "מגדר": "male",
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": "123",
                "שם משפחה": "כהן",
                "שנת לידה": "1980",
                "מגדר": "male",
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": "דני-danny",
                "שם משפחה": "כהן",
                "שנת לידה": "1980",
                "מגדר": "male",
                "מקצה": '10 ק"מ',
            },
        ]

    @staticmethod
    def get_malformed_years():
        """Get participants with malformed birth years."""
        return [
            {
                "שם פרטי": "דני",
                "שם משפחה": "כהן",
                "שנת לידה": "",
                "מגדר": "male",
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": "משה",
                "שם משפחה": "לוי",
                "שנת לידה": "abcd",
                "מגדר": "male",
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": "יוסי",
                "שם משפחה": "ישראלי",
                "שנת לידה": "1800",
                "מגדר": "male",
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": "דוד",
                "שם משפחה": "בן דוד",
                "שנת לידה": "2025",
                "מגדר": "male",
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": "שמעון",
                "שם משפחה": "פרץ",
                "שנת לידה": "15/10/1980",
                "מגדר": "male",
                "מקצה": '10 ק"מ',
            },
        ]

    @staticmethod
    def get_malformed_genders():
        """Get participants with malformed gender data."""
        return [
            {
                "שם פרטי": "דני",
                "שם משפחה": "כהן",
                "שנת לידה": "1980",
                "מגדר": "",
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": "משה",
                "שם משפחה": "לוי",
                "שנת לידה": "1975",
                "מגדר": "unknown",
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": "יוסי",
                "שם משפחה": "ישראלי",
                "שנת לידה": "1985",
                "מגדר": None,
                "מקצה": '10 ק"מ',
            },
            {
                "שם פרטי": "שרה",
                "שם משפחה": "לוי",
                "שנת לידה": "1982",
                "מגדר": "other",
                "מקצה": '10 ק"מ',
            },
        ]

    @staticmethod
    def get_malformed_races():
        """Get participants with malformed race categories."""
        return [
            {
                "שם פרטי": "דני",
                "שם משפחה": "כהן",
                "שנת לידה": "1980",
                "מגדר": "male",
                "מקצה": "",
            },
            {
                "שם פרטי": "משה",
                "שם משפחה": "לוי",
                "שנת לידה": "1975",
                "מגדר": "male",
                "מקצה": "unknown",
            },
            {
                "שם פרטי": "יוסי",
                "שם משפחה": "ישראלי",
                "שנת לידה": "1985",
                "מגדר": "male",
                "מקצה": None,
            },
            {
                "שם פרטי": "דוד",
                "שם משפחה": "בן דוד",
                "שנת לידה": "1990",
                "מגדר": "male",
                "מקצה": "123",
            },
        ]


# Utility functions for creating test data
def create_test_excel_file(file_path, scenario="default"):
    """Create a test Excel file based on scenario."""
    if scenario == "3plus":
        participants = SampleDataGenerator.generate_participants(
            count=20, age_range=(35, 55), gender_ratio=0.7, seed=42
        )
    elif scenario == "large":
        participants = SampleDataGenerator.generate_participants(
            count=500, age_range=(20, 70), gender_ratio=0.5, seed=42
        )
    else:
        participants = SampleDataGenerator.generate_participants(count=50, seed=42)

    results = SampleDataGenerator.generate_race_results(
        participants, num_results_per_person=2, seed=42
    )

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        participants.to_excel(writer, sheet_name="Participants", index=False)
        results.to_excel(writer, sheet_name="Results", index=False)

    return file_path


def create_empty_excel_file(file_path):
    """Create an empty Excel file for testing."""
    empty_df = pd.DataFrame()
    empty_df.to_excel(file_path, engine="openpyxl", index=False)
    return file_path


def create_corrupted_excel_file(file_path):
    """Create a corrupted Excel file for testing error handling."""
    with open(file_path, "wb") as f:
        f.write(b"This is not a valid Excel file")
    return file_path
