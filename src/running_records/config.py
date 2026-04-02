"""
===============================================================================
Project: Running Records Analysis
Module: Configuration Management
Description: Environment-based configuration management for the running records package.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
===============================================================================
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
import yaml
from dataclasses import dataclass, field


@dataclass
class ScrapingConfig:
    """Configuration for web scraping operations."""
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    respect_robots_txt: bool = True
    request_delay: float = 0.5


@dataclass
class DatabaseConfig:
    """Configuration for database operations."""
    url: Optional[str] = None
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class ExcelConfig:
    """Configuration for Excel file operations."""
    output_dir: str = "excel"
    max_rows_per_sheet: int = 1000000
    include_charts: bool = False
    auto_filter: bool = True


@dataclass
class WebAppConfig:
    """Configuration for web applications."""
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = False
    secret_key: Optional[str] = None
    upload_folder: str = "uploads"
    max_content_length: int = 16 * 1024 * 1024  # 16MB


@dataclass
class Config:
    """Main configuration class."""
    # Environment
    environment: str = "development"
    
    # Component configurations
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    excel: ExcelConfig = field(default_factory=ExcelConfig)
    webapp: WebAppConfig = field(default_factory=WebAppConfig)
    
    # Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "data")
    
    # Feature flags
    enable_caching: bool = True
    enable_logging: bool = True
    enable_metrics: bool = False
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        Path(self.excel.output_dir).mkdir(exist_ok=True)
        
        # Load environment-specific overrides
        self._load_environment_config()
        
        # Load from environment variables
        self._load_env_overrides()
    
    def _load_environment_config(self) -> None:
        """Load configuration from environment-specific YAML file."""
        config_file = self.project_root / "config" / f"{self.environment}.yaml"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                env_config = yaml.safe_load(f)
                self._update_from_dict(env_config)
    
    def _load_env_overrides(self) -> None:
        """Load configuration overrides from environment variables."""
        # Web app overrides
        if os.getenv("FLASK_SECRET_KEY"):
            self.webapp.secret_key = os.getenv("FLASK_SECRET_KEY")
        
        if os.getenv("FLASK_DEBUG"):
            self.webapp.debug = os.getenv("FLASK_DEBUG").lower() in ("true", "1", "yes")
        
        if os.getenv("FLASK_HOST"):
            self.webapp.host = os.getenv("FLASK_HOST")
        
        if os.getenv("FLASK_PORT"):
            self.webapp.port = int(os.getenv("FLASK_PORT"))
        
        # Database overrides
        if os.getenv("DATABASE_URL"):
            self.database.url = os.getenv("DATABASE_URL")
        
        # Scraping overrides
        if os.getenv("SCRAPING_TIMEOUT"):
            self.scraping.timeout = int(os.getenv("SCRAPING_TIMEOUT"))
        
        if os.getenv("SCRAPING_MAX_RETRIES"):
            self.scraping.max_retries = int(os.getenv("SCRAPING_MAX_RETRIES"))
        
        # Excel overrides
        if os.getenv("EXCEL_OUTPUT_DIR"):
            self.excel.output_dir = os.getenv("EXCEL_OUTPUT_DIR")
    
    def _update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if "scraping" in config_dict:
            self._update_dataclass(self.scraping, config_dict["scraping"])
        
        if "database" in config_dict:
            self._update_dataclass(self.database, config_dict["database"])
        
        if "excel" in config_dict:
            self._update_dataclass(self.excel, config_dict["excel"])
        
        if "webapp" in config_dict:
            self._update_dataclass(self.webapp, config_dict["webapp"])
        
        # Update top-level fields
        for key, value in config_dict.items():
            if hasattr(self, key) and not callable(getattr(self, key)):
                setattr(self, key, value)
    
    def _update_dataclass(self, obj: Any, updates: Dict[str, Any]) -> None:
        """Update dataclass fields from dictionary."""
        for key, value in updates.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    @classmethod
    def from_env(cls, environment: Optional[str] = None) -> "Config":
        """Create configuration from environment."""
        if environment is None:
            environment = os.getenv("RUNNING_RECORDS_ENV", "development")
        
        return cls(environment=environment)
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == "testing"


# Global configuration instance
config = Config.from_env()
