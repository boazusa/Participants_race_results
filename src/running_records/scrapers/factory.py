"""
===============================================================================
Project: Running Records Analysis
Module: Scraper Factory
Description: Factory for creating appropriate scrapers based on URL.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
===============================================================================
"""

from typing import Optional
from urllib.parse import urlparse

from .base import BaseScraper
from .threeplus import ThreePlusScraper
from .realtiming import RealTimingScraper
from .modiin import ModiinScraper
from .shvoong import ShvoongScraper
from ..exceptions import ScraperNotFoundError, UnsupportedURLError


class ScraperFactory:
    """
    Factory class for creating appropriate scrapers based on URL patterns.
    """
    
    # Mapping of domain patterns to scraper classes
    _SCRAPER_MAPPING = {
        '3plus.co.il': ThreePlusScraper,
        'realtiming.co.il': RealTimingScraper,
        'matnasmodiin.org.il': ModiinScraper,
        'ashkelon.runisrael.org.il': ModiinScraper,  # Uses same scraper as Modiin
        'shvoong.co.il': ShvoongScraper,
        'raceresults.shvoong.co.il': ShvoongScraper,
    }
    
    @classmethod
    def create_scraper(cls, url: str, **kwargs) -> BaseScraper:
        """
        Create appropriate scraper for the given URL.
        
        Args:
            url: URL to scrape
            **kwargs: Additional arguments for scraper initialization
            
        Returns:
            Appropriate scraper instance
            
        Raises:
            ScraperNotFoundError: If no suitable scraper found
            UnsupportedURLError: If URL is not supported
        """
        if not url:
            raise UnsupportedURLError("URL cannot be empty", url)
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Find matching scraper
            for pattern, scraper_class in cls._SCRAPER_MAPPING.items():
                if pattern in domain:
                    return scraper_class(**kwargs)
            
            # No scraper found
            supported_domains = list(cls._SCRAPER_MAPPING.keys())
            raise UnsupportedURLError(
                f"No scraper found for domain: {domain}",
                url,
                supported_domains
            )
            
        except Exception as e:
            if isinstance(e, (ScraperNotFoundError, UnsupportedURLError)):
                raise
            raise ScraperNotFoundError(f"Failed to create scraper for URL {url}: {str(e)}", url)
    
    @classmethod
    def get_supported_domains(cls) -> list:
        """
        Get list of supported domains.
        
        Returns:
            List of supported domain patterns
        """
        return list(cls._SCRAPER_MAPPING.keys())
    
    @classmethod
    def is_url_supported(cls, url: str) -> bool:
        """
        Check if URL is supported by any scraper.
        
        Args:
            url: URL to check
            
        Returns:
            True if supported, False otherwise
        """
        try:
            cls.create_scraper(url)
            return True
        except (ScraperNotFoundError, UnsupportedURLError):
            return False
    
    @classmethod
    def register_scraper(cls, domain_pattern: str, scraper_class: type) -> None:
        """
        Register a new scraper for a domain pattern.
        
        Args:
            domain_pattern: Domain pattern to match
            scraper_class: Scraper class to use
        """
        if not issubclass(scraper_class, BaseScraper):
            raise ValueError("Scraper class must inherit from BaseScraper")
        
        cls._SCRAPER_MAPPING[domain_pattern.lower()] = scraper_class
    
    @classmethod
    def unregister_scraper(cls, domain_pattern: str) -> None:
        """
        Unregister a scraper for a domain pattern.
        
        Args:
            domain_pattern: Domain pattern to remove
        """
        pattern = domain_pattern.lower()
        if pattern in cls._SCRAPER_MAPPING:
            del cls._SCRAPER_MAPPING[pattern]
