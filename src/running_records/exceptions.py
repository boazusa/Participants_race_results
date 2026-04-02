"""
===============================================================================
Project: Running Records Analysis
Module: Custom Exceptions
Description: Custom exception hierarchy for the running records package.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
==============================================================================="""


class RunningRecordsError(Exception):
    """Base exception for all running records errors."""
    pass


class ScrapingError(RunningRecordsError):
    """Base exception for scraping-related errors."""
    pass


class NetworkError(ScrapingError):
    """Raised when network operations fail."""
    def __init__(self, message: str, url: str, status_code: int = None, original_error: Exception = None):
        super().__init__(message)
        self.url = url
        self.status_code = status_code
        self.original_error = original_error


class TimeoutError(NetworkError):
    """Raised when network operations timeout."""
    pass


class ConnectionError(NetworkError):
    """Raised when connection to server fails."""
    pass


class HTTPError(NetworkError):
    """Raised when HTTP request returns error status."""
    pass


class ParseError(ScrapingError):
    """Raised when HTML parsing fails."""
    def __init__(self, message: str, url: str, html_snippet: str = None):
        super().__init__(message)
        self.url = url
        self.html_snippet = html_snippet


class TableNotFoundError(ParseError):
    """Raised when expected table is not found in HTML."""
    pass


class DataValidationError(RunningRecordsError):
    """Raised when data validation fails."""
    def __init__(self, message: str, field: str = None, value: any = None):
        super().__init__(message)
        self.field = field
        self.value = value


class InvalidYearError(DataValidationError):
    """Raised when birth year validation fails."""
    pass


class InvalidDistanceError(DataValidationError):
    """Raised when distance normalization fails."""
    pass


class InvalidTimeError(DataValidationError):
    """Raised when time string validation fails."""
    pass


class FilterError(RunningRecordsError):
    """Raised when participant filtering fails."""
    def __init__(self, message: str, filter_params: dict = None):
        super().__init__(message)
        self.filter_params = filter_params


class AnalysisError(RunningRecordsError):
    """Raised when race analysis operations fail."""
    def __init__(self, message: str, participant_name: str = None):
        super().__init__(message)
        self.participant_name = participant_name


class ExportError(RunningRecordsError):
    """Raised when data export operations fail."""
    def __init__(self, message: str, file_path: str = None, format_type: str = None):
        super().__init__(message)
        self.file_path = file_path
        self.format_type = format_type


class ExcelExportError(ExportError):
    """Raised when Excel export operations fail."""
    pass


class ConfigurationError(RunningRecordsError):
    """Raised when configuration is invalid."""
    def __init__(self, message: str, config_key: str = None, config_value: any = None):
        super().__init__(message)
        self.config_key = config_key
        self.config_value = config_value


class ScraperNotFoundError(ScrapingError):
    """Raised when no suitable scraper is found for a URL."""
    def __init__(self, message: str, url: str):
        super().__init__(message)
        self.url = url


class UnsupportedURLError(ScrapingError):
    """Raised when URL is not supported by any scraper."""
    def __init__(self, message: str, url: str, supported_domains: list = None):
        super().__init__(message)
        self.url = url
        self.supported_domains = supported_domains or []


class ParticipantNotFoundError(RunningRecordsError):
    """Raised when no participants are found for given criteria."""
    def __init__(self, message: str, criteria: dict = None):
        super().__init__(message)
        self.criteria = criteria


class ResultsNotFoundError(RunningRecordsError):
    """Raised when no race results are found for a participant."""
    def __init__(self, message: str, participant_name: str = None):
        super().__init__(message)
        self.participant_name = participant_name


class FileOperationError(RunningRecordsError):
    """Raised when file operations fail."""
    def __init__(self, message: str, file_path: str = None, operation: str = None):
        super().__init__(message)
        self.file_path = file_path
        self.operation = operation


class AuthenticationError(RunningRecordsError):
    """Raised when authentication fails (for future use)."""
    pass


class PermissionError(RunningRecordsError):
    """Raised when permission is denied for an operation."""
    pass


class RateLimitError(NetworkError):
    """Raised when rate limiting is detected."""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class ServiceUnavailableError(NetworkError):
    """Raised when external service is unavailable."""
    pass
