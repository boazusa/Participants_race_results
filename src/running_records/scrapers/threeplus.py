"""
===============================================================================
Project: Running Records Analysis
Module: ThreePlus Scraper
Description: Scraper for 3plus.co.il race result websites.
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
from typing import List, Tuple, Dict, Any
from urllib.parse import quote

from .base import BaseScraper
from ..exceptions import ParseError, TableNotFoundError


class ThreePlusScraper(BaseScraper):
    """
    Scraper for 3plus.co.il race result websites.
    
    Handles participant tables with ID 'm_ph4wp1_tblData' and individual
    result searches via shvoong.co.il.
    """
    
    def scrape_participants(self, url: str) -> pd.DataFrame:
        """
        Scrape participants table from 3plus website.
        
        Args:
            url: URL of the participants page
            
        Returns:
            DataFrame containing participants data
        """
        try:
            # Make HTTP request
            response = self._make_request(url)
            soup = self._parse_html(response.text)
            
            # Extract table data
            table_data = self._extract_table_data(soup, '#m_ph4wp1_tblData')
            
            # Clean and normalize data
            df = self._clean_participant_data(table_data)
            
            return df
            
        except Exception as e:
            if isinstance(e, (ParseError, TableNotFoundError)):
                raise
            raise ParseError(f"Failed to scrape 3plus participants: {str(e)}", url)
    
    def compute_best_results(
        self,
        names: List[Tuple[str, str]],
        category: str,
        years_back: int = 5
    ) -> pd.DataFrame:
        """
        Compute best results for participants by searching shvoong.co.il.
        
        Args:
            names: List of (first_name, last_name) tuples
            category: Race category to search for
            years_back: Number of years back to search
            
        Returns:
            DataFrame containing best results
        """
        all_results = []
        
        for first_name, last_name in names:
            try:
                # Search for participant results
                results = self._search_participant_results(first_name, last_name)
                
                if results:
                    # Filter by category and date
                    filtered_results = self._filter_results(results, category, years_back)
                    
                    # Get best result
                    if filtered_results:
                        best_result = self._get_best_result(filtered_results)
                        best_result['שם פרטי'] = first_name
                        best_result['שם משפחה'] = last_name
                        all_results.append(best_result)
                        
            except Exception as e:
                # Log error but continue with other participants
                print(f"Error searching for {first_name} {last_name}: {str(e)}")
                continue
        
        return pd.DataFrame(all_results)
    
    def get_supported_domains(self) -> List[str]:
        """
        Get list of supported domains for this scraper.
        
        Returns:
            List of domain strings
        """
        return ['3plus.co.il']
    
    def _search_participant_results(self, first_name: str, last_name: str) -> List[Dict[str, str]]:
        """
        Search for participant results on shvoong.co.il.
        
        Args:
            first_name: Participant's first name
            last_name: Participant's last name
            
        Returns:
            List of result dictionaries
        """
        # Build search URL
        search_url = self._build_search_url(first_name, last_name)
        
        try:
            # Make search request
            response = self._make_request(search_url)
            soup = self._parse_html(response.text)
            
            # Extract results table
            results_data = self._extract_results_table(soup)
            
            return self._clean_results_data(results_data)
            
        except Exception as e:
            print(f"Error searching shvoong for {first_name} {last_name}: {str(e)}")
            return []
    
    def _build_search_url(self, first_name: str, last_name: str) -> str:
        """
        Build shvoong search URL for participant.
        
        Args:
            first_name: Participant's first name
            last_name: Participant's last name
            
        Returns:
            Search URL
        """
        # Encode search query
        query = f"{first_name} {last_name}"
        encoded_query = quote(query)
        
        return f"https://raceresults.shvoong.co.il/race-result/?q={encoded_query}"
    
    def _extract_results_table(self, soup: Any) -> List[Dict[str, str]]:
        """
        Extract results table from shvoong search page.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of result dictionaries
        """
        # Look for results table (various possible selectors)
        selectors = [
            'table.race-results',
            'table.results-table',
            'table',
        ]
        
        for selector in selectors:
            try:
                table_data = self._extract_table_data(soup, selector)
                if table_data:
                    return table_data
            except TableNotFoundError:
                continue
        
        return []
    
    def _filter_results(self, results: List[Dict[str, str]], category: str, years_back: int) -> List[Dict[str, str]]:
        """
        Filter results by category and date.
        
        Args:
            results: List of result dictionaries
            category: Race category
            years_back: Number of years back to keep
            
        Returns:
            Filtered list of results
        """
        if not results:
            return []
        
        df = pd.DataFrame(results)
        
        # Filter by category
        df = self._filter_results_by_category(df, category)
        
        # Filter by date
        df = self._filter_results_by_date(df, years_back)
        
        return df.to_dict('records')
    
    def _get_best_result(self, results: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Get the best (fastest) result from a list of results.
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Best result dictionary
        """
        if not results:
            return {}
        
        df = pd.DataFrame(results)
        
        # Convert times to seconds for comparison
        if 'תוצאה מיטבית' in df.columns:
            df['time_seconds'] = df['תוצאה מיטבית'].apply(self._time_to_seconds)
            
            # Sort by time (fastest first)
            df = df.sort_values('time_seconds')
            
            # Return the best result
            best_result = df.iloc[0].to_dict()
            
            # Remove temporary column
            if 'time_seconds' in best_result:
                del best_result['time_seconds']
            
            return best_result
        
        # If no time column, return first result
        return results[0]
    
    def _time_to_seconds(self, time_str: str) -> float:
        """
        Convert time string to seconds for comparison.
        
        Args:
            time_str: Time string (HH:MM:SS format)
            
        Returns:
            Time in seconds
        """
        try:
            if pd.isna(time_str) or not time_str:
                return float('inf')
            
            parts = str(time_str).split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            else:
                return float('inf')
                
        except (ValueError, TypeError):
            return float('inf')
    
    def _get_column_mapping(self) -> Dict[str, str]:
        """
        Get column name mapping for 3plus participants table.
        
        Returns:
            Dictionary mapping raw column names to standard names
        """
        return {
            'מקום': 'מקום',
            'שם פרטי': 'שם פרטי',
            'שם משפחה': 'שם משפחה',
            'שנת לידה': 'שנת לידה',
            'מגדר': 'מגדר',
            'מקצה': 'מקצה',
            'קבוצה': 'קבוצה',
        }
    
    def _get_results_column_mapping(self) -> Dict[str, str]:
        """
        Get column name mapping for shvoong results table.
        
        Returns:
            Dictionary mapping raw column names to standard names
        """
        return {
            'תאריך': 'תאריך',
            'מקום': 'מקום',
            'שם פרטי': 'שם פרטי',
            'שם משפחה': 'שם משפחה',
            'מקצה': 'מקצה',
            'תוצאה': 'תוצאה',
            'זמן אישי': 'זמן אישי',
            'מיקום כללי': 'מיקום כללי',
            'מיקום בקבוצה': 'מיקום בקבוצה',
        }
