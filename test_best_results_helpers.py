#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Test Suite - Best Results Helpers
Description: Unit and integration tests for helper functions used in the
             best_results_3plus_or_realtiming_race module.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 15/11/2025
Last Modified: 24/11/2025
Version: 1.0.0
Python Version: 3.8+
Dependencies:
    - unittest (standard library)
    - pandas >= 1.3.0 (for test data manipulation)
    - pytest >= 6.2.5 (for test discovery and running)
Performance: Lightweight tests designed for frequent execution during development.
             Test execution time should be minimal.
License: [boazusa@hotmail.com]
===============================================================================
"""

import unittest
import pandas as pd
import sys
import os

# Add the parent directory to the path to allow importing the module under test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import the module to be tested
import best_results_3plus_or_realtiming_race as br
from best_results_3plus_or_realtiming_race import best_race_results_per_participant


class TestNormalizeDistance(unittest.TestCase):
    def test_10k_variants(self):
        f = best_race_results_per_participant.normalize_distance
        self.assertEqual(f("10 ק\"מ"), "10K")
        self.assertEqual(f("10ק\"מ"), "10K")
        self.assertEqual(f("9800"), "10K")
        self.assertEqual(f("10000"), "10K")

    def test_21k_variants(self):
        f = best_race_results_per_participant.normalize_distance
        self.assertEqual(f("21097"), "21K")
        self.assertEqual(f("21000"), "21K")
        self.assertEqual(f("21K"), "21K")

    def test_5k_and_15k_detection(self):
        f = best_race_results_per_participant.normalize_distance
        self.assertEqual(f("15 ק\"מ"), "15K")
        self.assertEqual(f("5 ק\"מ"), "5K")

    def test_empty_or_nan(self):
        f = best_race_results_per_participant.normalize_distance
        self.assertTrue(pd.isna(f("")))
        self.assertTrue(pd.isna(f(None)))

    def test_42k_variants(self):
        f = best_race_results_per_participant.normalize_distance
        self.assertEqual(f("42195"), "42K")
        self.assertEqual(f("42K"), "42K")
        self.assertEqual(f("42k"), "42K")

    def test_unknown_string_returns_nan(self):
        f = best_race_results_per_participant.normalize_distance
        self.assertTrue(pd.isna(f("unknown distance")))

    def test_numeric_inputs(self):
        f = best_race_results_per_participant.normalize_distance
        self.assertEqual(f(10000), "10K")
        self.assertEqual(f(21097), "21K")


class TestChooseBestTimeString(unittest.TestCase):
    def test_prefers_personal_time_over_result(self):
        row = pd.Series({"זמן אישי": "00:40:00", "תוצאה": "00:41:00"})
        result = best_race_results_per_participant.choose_best_time_string(row)
        self.assertEqual(result, "00:40:00")

    def test_falls_back_to_result_if_personal_is_zero(self):
        row = pd.Series({"זמן אישי": "00:00:00", "תוצאה": "00:41:00"})
        result = best_race_results_per_participant.choose_best_time_string(row)
        self.assertEqual(result, "00:41:00")

    def test_returns_empty_when_both_invalid(self):
        row = pd.Series({"זמן אישי": "00:00:00", "תוצאה": "00:00:00"})
        result = best_race_results_per_participant.choose_best_time_string(row)
        self.assertEqual(result, "")

    def test_uses_result_when_personal_missing(self):
        row = pd.Series({"תוצאה": "00:42:00"})
        result = best_race_results_per_participant.choose_best_time_string(row)
        self.assertEqual(result, "00:42:00")

    def test_treats_nat_and_none_strings_as_invalid(self):
        row = pd.Series({"זמן אישי": "NaT", "תוצאה": "None"})
        result = best_race_results_per_participant.choose_best_time_string(row)
        self.assertEqual(result, "")

    def test_empty_series_returns_empty_string(self):
        row = pd.Series({})
        result = best_race_results_per_participant.choose_best_time_string(row)
        self.assertEqual(result, "")


"""
python -m unittest test_best_results_helpers.py
"""

if __name__ == "__main__":
    unittest.main()
