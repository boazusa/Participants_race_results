"""
===============================================================================
Project: Running Records Analysis
Module: RealTiming Scraper
Description: Scraper for RealTiming.co.il race result websites.
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
from typing import List, Tuple

from .base import BaseScraper
from ..exceptions import ParseError, TableNotFoundError


class RealTimingScraper(BaseScraper):
    """
    Scraper for RealTiming.co.il race result websites.
    
    Handles participant tables similar to 3plus sites.
    """
    
    def scrape_participants(self, url: str) -> pd.DataFrame:
        """
        Scrape participants table from RealTiming website.
        
        Args:
            url: URL of the participants page
            
        Returns:
            DataFrame containing participants data
        """
        try:
            # Make HTTP request
            response = self._make_request(url)
            soup = self._parse_html(response.text)
            
            # Extract table data (RealTiming often uses similar table structure)
            table_data = self._extract_table_data(soup, 'table')
            
            # Clean and normalize data
            df = self._clean_participant_data(table_data)
            
            return df
            
        except Exception as e:
            if isinstance(e, (ParseError, TableNotFoundError)):
                raise
            raise ParseError(f"Failed to scrape RealTiming participants: {str(e)}", url)
    
    def compute_best_results(
        self,
        names: List[Tuple[str, str]],
        category: str,
        years_back: int = 5
    ) -> pd.DataFrame:
        """
        Compute best results for participants.
        
        Args:
            names: List of (first_name, last_name) tuples
            category: Race category to search for
            years_back: Number of years back to search
            
        Returns:
            DataFrame containing best results
        """
        # For now, delegate to ThreePlus scraper logic
        # In a full implementation, this would use RealTiming-specific search
        from .threeplus import ThreePlusScraper
        
        threeplus_scraper = ThreePlusScraper()
        return threeplus_scraper.compute_best_results(names, category, years_back)
    
    def get_supported_domains(self) -> List[str]:
        """
        Get list of supported domains for this scraper.
        
        Returns:
            List of domain strings
        """
        return ['realtiming.co.il']
