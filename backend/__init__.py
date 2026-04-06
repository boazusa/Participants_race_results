#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Backend Package
Description: Backend logic package for race analysis, Excel processing, and 
             individual race results. Provides core functionality for the 
             running records analysis system.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 06/04/2026
Version: 1.0.0
Python Version: 3.8+
License: [boazusa@hotmail.com]
===============================================================================
"""

# Import main backend modules for easy access
from .race_analyzer import best_race_results_per_participant
from .excel_processor import *
from .person_results import fetch_and_process_results

__all__ = [
    'best_race_results_per_participant',
    'fetch_and_process_results'
]
