"""
===============================================================================
Project: Running Records Analysis
Module: Shvoong Scraper
Description: Scraper for Shvoong race result search websites.
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


class ShvoongScraper(BaseScraper):
    """
    Scraper for Shvoong race result search websites.
    
    Handles participant result searches on shvoong.co.il.
    """
    
    def scrape_participants(self, url: str) -> pd.DataFrame:
        """
        Shvoong is primarily for searching results, not participants.
        
        Args:
            url: URL (not applicable for Shvoong)
            
        Returns:
            Empty DataFrame
        """
        # Shvoong doesn't have participant tables, it's for searching results
        return pd.DataFrame()
    
    def compute_best_results(
        self,
        names: List[Tuple[str, str]],
        category: str,
        years_back: int = 5
    ) -> pd.DataFrame:
        """
        Compute best results for participants using Shvoong search.
        
        Args:
            names: List of (first_name, last_name) tuples
            category: Race category to search for
            years_back: Number of years back to search
            
        Returns:
            DataFrame containing best results
        """
        # Delegate to ThreePlus scraper which already has Shvoong integration
        from .threeplus import ThreePlusScraper
        
        threeplus_scraper = ThreePlusScraper()
        return threeplus_scraper.compute_best_results(names, category, years_back)
    
    def get_supported_domains(self) -> List[str]:
        """
        Get list of supported domains for this scraper.
        
        Returns:
            List of domain strings
        """
        return ['shvoong.co.il', 'raceresults.shvoong.co.il']
