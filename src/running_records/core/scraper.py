"""
===============================================================================
Project: Running Records Analysis
Module: Base Scraper
Description: Abstract base class for web scrapers.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
===============================================================================
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple
from urllib.parse import urljoin, urlparse
import time
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

from ..config import config
from ..exceptions import (
    ScrapingError,
    NetworkError,
    ParseError,
    TimeoutError,
    HTTPError,
    TableNotFoundError,
    ResultsNotFoundError
)
from ..utils.time_utils import parse_time_string, choose_best_time_string
from ..utils.normalization import normalize_year, normalize_distance, normalize_name


class BaseScraper(ABC):
    """
    Abstract base class for all race website scrapers.
    
    This class defines the interface that all scrapers must implement
    and provides common functionality for HTTP requests and data processing.
    """
    
    def __init__(self, timeout: Optional[int] = None, max_retries: Optional[int] = None):
        """
        Initialize the scraper.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout or config.scraping.timeout
        self.max_retries = max_retries or config.scraping.max_retries
        self.session = self._create_session()
    
    def _create_session(self) -> Any:
        """Create HTTP session with appropriate settings."""
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            
            # Configure retry strategy
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Set headers
            session.headers.update({
                'User-Agent': config.scraping.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            })
            
            return session
            
        except ImportError:
            raise ScrapingError("requests library is required for web scraping")
    
    def _make_request(self, url: str, **kwargs) -> Any:
        """
        Make HTTP request with error handling and retries.
        
        Args:
            url: URL to request
            **kwargs: Additional request parameters
            
        Returns:
            Response object
            
        Raises:
            NetworkError: If request fails
        """
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request timeout for {url}", url, original_error=e)
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection failed for {url}", url, original_error=e)
        except requests.exceptions.HTTPError as e:
            raise HTTPError(f"HTTP error for {url}: {e.response.status_code}", url, e.response.status_code, e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed for {url}: {str(e)}", url, original_error=e)
    
    def _parse_html(self, html_content: str) -> Any:
        """
        Parse HTML content into BeautifulSoup object.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            BeautifulSoup object
            
        Raises:
            ParseError: If HTML parsing fails
        """
        try:
            from bs4 import BeautifulSoup
            return BeautifulSoup(html_content, 'html.parser')
        except ImportError:
            raise ScrapingError("beautifulsoup4 library is required for HTML parsing")
        except Exception as e:
            raise ParseError(f"Failed to parse HTML: {str(e)}", "")
    
    @abstractmethod
    def scrape_participants(self, url: str) -> pd.DataFrame:
        """
        Scrape participants table from the given URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            DataFrame containing participants data
            
        Raises:
            ScrapingError: If scraping fails
        """
        pass
    
    @abstractmethod
    def compute_best_results(
        self,
        names: List[Tuple[str, str]],
        category: str,
        years_back: int = 5
    ) -> pd.DataFrame:
        """
        Compute best results for given participants.
        
        Args:
            names: List of (first_name, last_name) tuples
            category: Race category to search for
            years_back: Number of years back to search
            
        Returns:
            DataFrame containing best results
            
        Raises:
            ScrapingError: If computation fails
        """
        pass
    
    @abstractmethod
    def get_supported_domains(self) -> List[str]:
        """
        Get list of supported domains for this scraper.
        
        Returns:
            List of domain strings
        """
        pass
    
    def _extract_table_data(self, soup: Any, table_selector: str) -> List[Dict[str, str]]:
        """
        Extract data from HTML table.
        
        Args:
            soup: BeautifulSoup object
            table_selector: CSS selector for table
            
        Returns:
            List of dictionaries with table data
            
        Raises:
            TableNotFoundError: If table not found
        """
        table = soup.select_one(table_selector)
        if not table:
            raise TableNotFoundError(f"Table not found with selector: {table_selector}", "")
        
        # Extract headers
        headers = []
        header_row = table.find('tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        if not headers:
            raise TableNotFoundError("No headers found in table", "")
        
        # Extract data rows
        data_rows = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) == len(headers):
                row_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        row_data[headers[i]] = cell.get_text(strip=True)
                data_rows.append(row_data)
        
        return data_rows
    
    def _clean_participant_data(self, raw_data: List[Dict[str, str]]) -> pd.DataFrame:
        """
        Clean and normalize participant data.
        
        Args:
            raw_data: Raw participant data from scraping
            
        Returns:
            Cleaned DataFrame
        """
        if not raw_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(raw_data)
        
        # Standardize column names
        column_mapping = self._get_column_mapping()
        df = df.rename(columns=column_mapping)
        
        # Normalize data
        if 'שנת לידה' in df.columns:
            df['שנת לידה'] = df['שנת לידה'].apply(normalize_year)
        
        if 'שם פרטי' in df.columns:
            df['שם פרטי'] = df['שם פרטי'].apply(normalize_name)
        
        if 'שם משפחה' in df.columns:
            df['שם משפחה'] = df['שם משפחה'].apply(normalize_name)
        
        if 'מקצה' in df.columns:
            df['מקצה'] = df['מקצה'].apply(normalize_distance)
        
        # Remove rows with missing essential data
        essential_columns = ['שם פרטי', 'שם משפחה']
        for col in essential_columns:
            if col in df.columns:
                df = df[df[col].notna()]
        
        return df
    
    def _get_column_mapping(self) -> Dict[str, str]:
        """
        Get column name mapping for this scraper.
        
        Returns:
            Dictionary mapping raw column names to standard names
        """
        # Default mapping - override in subclasses as needed
        return {
            'מקום': 'מקום',
            'שם פרטי': 'שם פרטי',
            'שם משפחה': 'שם משפחה',
            'שנת לידה': 'שנת לידה',
            'מגדר': 'מגדר',
            'מקצה': 'מקצה',
            'קבוצה': 'קבוצה',
            'אגודה': 'קבוצה',
        }
    
    def _clean_results_data(self, raw_data: List[Dict[str, str]]) -> pd.DataFrame:
        """
        Clean and normalize race results data.
        
        Args:
            raw_data: Raw results data from scraping
            
        Returns:
            Cleaned DataFrame
        """
        if not raw_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(raw_data)
        
        # Standardize column names
        column_mapping = self._get_results_column_mapping()
        df = df.rename(columns=column_mapping)
        
        # Choose best time
        if all(col in df.columns for col in ['זמן אישי', 'תוצאה']):
            df['תוצאה מיטבית'] = df.apply(choose_best_time_string, axis=1)
        
        # Remove rows with missing essential data
        essential_columns = ['שם פרטי', 'שם משפחה', 'תוצאה מיטבית']
        for col in essential_columns:
            if col in df.columns:
                df = df[df[col].notna() & (df[col] != '')]
        
        return df
    
    def _get_results_column_mapping(self) -> Dict[str, str]:
        """
        Get results column name mapping for this scraper.
        
        Returns:
            Dictionary mapping raw column names to standard names
        """
        # Default mapping - override in subclasses as needed
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
    
    def _build_search_url(self, first_name: str, last_name: str) -> str:
        """
        Build search URL for finding participant results.
        
        Args:
            first_name: Participant's first name
            last_name: Participant's last name
            
        Returns:
            Search URL
        """
        # Override in subclasses
        raise NotImplementedError("Subclasses must implement _build_search_url")
    
    def _filter_results_by_category(self, df: pd.DataFrame, category: str) -> pd.DataFrame:
        """
        Filter results by race category.
        
        Args:
            df: Results DataFrame
            category: Category to filter by
            
        Returns:
            Filtered DataFrame
        """
        if 'מקצה' not in df.columns:
            return df
        
        # Convert category to search terms
        category_keywords = self._get_category_keywords(category)
        
        # Filter rows where race category matches
        mask = df['מקצה'].astype(str).str.contains(
            '|'.join(category_keywords), 
            case=False, 
            na=False
        )
        
        return df[mask]
    
    def _get_category_keywords(self, category: str) -> List[str]:
        """
        Get search keywords for a given category.
        
        Args:
            category: Standard category name (e.g., '10K')
            
        Returns:
            List of search keywords
        """
        keywords = {
            '5K': ['5', '5 ק"מ', '5ק"מ', '5000'],
            '10K': ['10', '10 ק"מ', '10ק"מ', '10000', '9800'],
            '15K': ['15', '15 ק"מ', '15ק"מ', '15000'],
            '21K': ['21', '21 ק"מ', '21ק"מ', '21097', '21000', 'חצי מרתון'],
            '42K': ['42', '42 ק"מ', '42ק"מ', '42195', 'מרתון'],
        }
        
        return keywords.get(category, [category])
    
    def _filter_results_by_date(self, df: pd.DataFrame, years_back: int) -> pd.DataFrame:
        """
        Filter results by date (keep only recent results).
        
        Args:
            df: Results DataFrame
            years_back: Number of years back to keep
            
        Returns:
            Filtered DataFrame
        """
        if 'תאריך' not in df.columns:
            return df
        
        cutoff_date = datetime.now().replace(year=datetime.now().year - years_back)
        
        # Try to parse dates and filter
        try:
            df['תאריך'] = pd.to_datetime(df['תאריך'], errors='coerce')
            df = df[df['תאריך'] >= cutoff_date]
            # Convert back to string format
            df['תאריך'] = df['תאריך'].dt.strftime('%d/%m/%Y')
        except Exception:
            # If date parsing fails, return original DataFrame
            pass
        
        return df
