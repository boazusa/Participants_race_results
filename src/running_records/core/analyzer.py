"""
===============================================================================
Project: Running Records Analysis
Module: Race Analyzer
Description: Main race analysis engine that coordinates scraping, filtering, and analysis.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
===============================================================================
"""

import pandas as pd
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from ..config import config
from ..exceptions import (
    AnalysisError, 
    FilterError, 
    ParticipantNotFoundError,
    ResultsNotFoundError
)
from ..utils.validation import validate_filter_parameters
from .scraper import BaseScraper
from .filter import ParticipantFilter
from .exporter import ExcelExporter
from ..scrapers.factory import ScraperFactory


class RaceAnalyzer:
    """
    Main race analysis engine that coordinates all operations.
    
    This class serves as the main interface for race analysis operations,
    combining scraping, filtering, and result computation.
    """
    
    def __init__(
        self,
        url: str,
        race_name: Optional[str] = None,
        excel_path: Optional[str] = None,
        years_back: int = 5,
        scraper: Optional[BaseScraper] = None
    ):
        """
        Initialize the race analyzer.
        
        Args:
            url: URL of the race participants page
            race_name: Name of the race for output files
            excel_path: Path for Excel output file
            years_back: Number of years back to filter results
            scraper: Custom scraper instance (auto-detected if None)
        """
        # Normalize URL
        self.url = url.replace("view-source:", "")
        self.race_name = race_name or "Race"
        self.excel_path = excel_path
        self.years_back = years_back
        
        # Initialize components
        self.scraper = scraper or ScraperFactory.create_scraper(self.url)
        self.filter = ParticipantFilter()
        self.exporter = ExcelExporter()
        
        # Data storage
        self.participants_df: Optional[pd.DataFrame] = None
        self.filtered_names: Optional[List[Tuple[str, str]]] = None
        self.results_df: Optional[pd.DataFrame] = None
        
        # Filter parameters (for filename generation)
        self.min_year_param: Optional[int] = None
        self.max_year_param: Optional[int] = None
        
        # Ensure output directory exists
        Path(config.excel.output_dir).mkdir(exist_ok=True)
    
    def scrape_participants(self) -> pd.DataFrame:
        """
        Scrape participants data from the race URL.
        
        Returns:
            DataFrame containing participants data
            
        Raises:
            AnalysisError: If scraping fails
        """
        try:
            self.participants_df = self.scraper.scrape_participants(self.url)
            return self.participants_df
        except Exception as e:
            raise AnalysisError(f"Failed to scrape participants: {str(e)}")
    
    def get_filtered_names(
        self,
        min_year: int,
        max_year: int,
        gender: Optional[str] = None,
        race_keyword: Optional[str] = None
    ) -> List[Tuple[str, str]]:
        """
        Filter participants based on criteria.
        
        Args:
            min_year: Minimum birth year
            max_year: Maximum birth year
            gender: Gender filter ('male' or 'female')
            race_keyword: Keyword to filter race categories
            
        Returns:
            List of (first_name, last_name) tuples
            
        Raises:
            FilterError: If filtering fails
            ParticipantNotFoundError: If no participants match criteria
        """
        if self.participants_df is None:
            raise AnalysisError("No participants data available. Call scrape_participants() first.")
        
        # Store filter parameters for filename generation
        self.min_year_param = min_year
        self.max_year_param = max_year
        
        try:
            self.filtered_names = self.filter.filter_participants(
                self.participants_df,
                min_year=min_year,
                max_year=max_year,
                gender=gender,
                race_keyword=race_keyword
            )
            
            if not self.filtered_names:
                raise ParticipantNotFoundError(
                    "No participants found matching the specified criteria",
                    criteria={"min_year": min_year, "max_year": max_year, "gender": gender, "race_keyword": race_keyword}
                )
            
            return self.filtered_names
            
        except Exception as e:
            if isinstance(e, (FilterError, ParticipantNotFoundError)):
                raise
            raise FilterError(f"Failed to filter participants: {str(e)}")
    
    def compute_best_results(self, category: str) -> pd.DataFrame:
        """
        Compute best results for filtered participants in specified category.
        
        Args:
            category: Race category (e.g., '10K', '21K')
            
        Returns:
            DataFrame with best results
            
        Raises:
            AnalysisError: If computation fails
            ResultsNotFoundError: If no results found
        """
        if self.filtered_names is None:
            raise AnalysisError("No filtered participants available. Call get_filtered_names() first.")
        
        try:
            self.results_df = self.scraper.compute_best_results(
                self.filtered_names,
                category,
                years_back=self.years_back
            )
            
            if self.results_df.empty:
                raise ResultsNotFoundError(
                    "No race results found for filtered participants",
                    participant_name=f"{len(self.filtered_names)} participants"
                )
            
            return self.results_df
            
        except Exception as e:
            if isinstance(e, (ResultsNotFoundError, AnalysisError)):
                raise
            raise AnalysisError(f"Failed to compute best results: {str(e)}")
    
    def export_to_excel(self, category: str, output_path: Optional[str] = None) -> str:
        """
        Export results to Excel file.
        
        Args:
            category: Race category for filename
            output_path: Custom output path (auto-generated if None)
            
        Returns:
            Path to generated Excel file
            
        Raises:
            AnalysisError: If export fails
        """
        if self.results_df is None:
            raise AnalysisError("No results available. Call compute_best_results() first.")
        
        try:
            if output_path is None:
                # Generate filename based on race details
                age_range = f"{datetime.now().year - self.max_year_param}-{datetime.now().year - self.min_year_param}"
                output_path = self.exporter.generate_filename(
                    self.race_name,
                    category,
                    age_range
                )
            
            file_path = self.exporter.export_results(
                self.results_df,
                output_path,
                race_name=self.race_name,
                category=category
            )
            
            return file_path
            
        except Exception as e:
            raise AnalysisError(f"Failed to export results: {str(e)}")
    
    def run_complete_analysis(
        self,
        min_year: int,
        max_year: int,
        gender: Optional[str] = None,
        race_keyword: Optional[str] = None,
        category: str = "10K",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run complete analysis pipeline.
        
        Args:
            min_year: Minimum birth year
            max_year: Maximum birth year
            gender: Gender filter
            race_keyword: Race keyword filter
            category: Category for best results
            output_path: Custom output path
            
        Returns:
            Dictionary with analysis results and file paths
            
        Raises:
            AnalysisError: If any step fails
        """
        results = {
            "success": False,
            "participants_count": 0,
            "filtered_count": 0,
            "results_count": 0,
            "excel_file": None,
            "errors": []
        }
        
        try:
            # Step 1: Scrape participants
            participants_df = self.scrape_participants()
            results["participants_count"] = len(participants_df)
            
            # Step 2: Filter participants
            filtered_names = self.get_filtered_names(
                min_year=min_year,
                max_year=max_year,
                gender=gender,
                race_keyword=race_keyword
            )
            results["filtered_count"] = len(filtered_names)
            
            # Step 3: Compute best results
            results_df = self.compute_best_results(category)
            results["results_count"] = len(results_df)
            
            # Step 4: Export to Excel
            excel_file = self.export_to_excel(category, output_path)
            results["excel_file"] = excel_file
            
            results["success"] = True
            
        except Exception as e:
            results["errors"].append(str(e))
            raise
        
        return results
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Get summary of current analysis state.
        
        Returns:
            Dictionary with analysis summary
        """
        summary = {
            "url": self.url,
            "race_name": self.race_name,
            "years_back": self.years_back,
            "scraper_type": type(self.scraper).__name__,
            "participants_loaded": self.participants_df is not None,
            "participants_count": len(self.participants_df) if self.participants_df is not None else 0,
            "filtered_names_available": self.filtered_names is not None,
            "filtered_count": len(self.filtered_names) if self.filtered_names is not None else 0,
            "results_available": self.results_df is not None,
            "results_count": len(self.results_df) if self.results_df is not None else 0,
        }
        
        return summary


# Legacy compatibility alias
best_race_results_per_participant = RaceAnalyzer
