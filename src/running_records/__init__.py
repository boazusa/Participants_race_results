"""
===============================================================================
Project: Running Records Analysis
Package: running_records
Description: Python package for race result analysis and participant data processing.
             Provides tools for scraping race data, filtering participants, and 
             computing best results across multiple race websites.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
===============================================================================
"""

__version__ = "2.0.0"
__author__ = "Boaz Bilgory"
__email__ = "boazusa@hotmail.com"

# Core classes and functions
from .core.analyzer import RaceAnalyzer
from .core.scraper import BaseScraper
from .core.exporter import ExcelExporter

# Models
from .models.participant import Participant
from .models.race import Race
from .models.result import RaceResult

# Utilities
from .utils.normalization import normalize_year, normalize_distance
from .utils.time_utils import choose_best_time_string

# Configuration
from .config import Config

# Factory functions
from .scrapers.factory import ScraperFactory

# Legacy compatibility - maintain old class name
from .core.analyzer import RaceAnalyzer as best_race_results_per_participant

__all__ = [
    # Main classes
    "RaceAnalyzer",
    "BaseScraper", 
    "ExcelExporter",
    "best_race_results_per_participant",  # Legacy compatibility
    
    # Models
    "Participant",
    "Race", 
    "RaceResult",
    
    # Utilities
    "normalize_year",
    "normalize_distance",
    "choose_best_time_string",
    
    # Configuration and factories
    "Config",
    "ScraperFactory",
]
