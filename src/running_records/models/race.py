"""
===============================================================================
Project: Running Records Analysis
Module: Race Model
Description: Data model for race events.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime, date

from ..exceptions import DataValidationError
from ..utils.validation import validate_race_data


@dataclass
class Race:
    """
    Data model for a race event.
    """
    
    name: str
    date: Optional[date] = None
    location: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    participants_count: Optional[int] = None
    
    # Additional metadata
    description: Optional[str] = None
    organizer: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Normalize date
        if isinstance(self.date, str):
            try:
                self.date = datetime.strptime(self.date, "%Y-%m-%d").date()
            except ValueError:
                try:
                    self.date = datetime.strptime(self.date, "%d/%m/%Y").date()
                except ValueError:
                    self.date = None
        
        # Normalize name and location
        self.name = self.name.strip() if self.name else ""
        self.location = self.location.strip() if self.location else ""
        self.url = self.url.strip() if self.url else ""
    
    def validate(self) -> Dict[str, List[str]]:
        """
        Validate race data.
        
        Returns:
            Dictionary of validation errors
        """
        data = {
            "name": self.name,
            "date": self.date.isoformat() if self.date else "",
            "location": self.location,
        }
        
        return validate_race_data(data)
    
    def is_valid(self) -> bool:
        """
        Check if race data is valid.
        
        Returns:
            True if valid, False otherwise
        """
        errors = self.validate()
        return len(errors) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert race to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "date": self.date.isoformat() if self.date else None,
            "location": self.location,
            "url": self.url,
            "category": self.category,
            "participants_count": self.participants_count,
            "description": self.description,
            "organizer": self.organizer,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Race":
        """
        Create race from dictionary.
        
        Args:
            data: Dictionary with race data
            
        Returns:
            Race instance
        """
        return cls(
            name=data.get("name", ""),
            date=data.get("date"),
            location=data.get("location"),
            url=data.get("url"),
            category=data.get("category"),
            participants_count=data.get("participants_count"),
            description=data.get("description"),
            organizer=data.get("organizer"),
        )
    
    def get_display_date(self) -> str:
        """
        Get formatted date for display.
        
        Returns:
            Formatted date string
        """
        if self.date:
            return self.date.strftime("%d/%m/%Y")
        return "Unknown"
    
    def get_year(self) -> Optional[int]:
        """
        Get race year.
        
        Returns:
            Year as integer or None
        """
        return self.date.year if self.date else None
    
    def is_past(self) -> bool:
        """
        Check if race is in the past.
        
        Returns:
            True if race date is before today
        """
        if self.date:
            return self.date < date.today()
        return False
    
    def is_future(self) -> bool:
        """
        Check if race is in the future.
        
        Returns:
            True if race date is after today
        """
        if self.date:
            return self.date > date.today()
        return False
    
    def days_until(self) -> Optional[int]:
        """
        Get days until race (for future races).
        
        Returns:
            Number of days until race, or None if not applicable
        """
        if self.date and self.is_future():
            return (self.date - date.today()).days
        return None
    
    def days_since(self) -> Optional[int]:
        """
        Get days since race (for past races).
        
        Returns:
            Number of days since race, or None if not applicable
        """
        if self.date and self.is_past():
            return (date.today() - self.date).days
        return None
    
    def __str__(self) -> str:
        """String representation."""
        parts = [self.name]
        if self.date:
            parts.append(self.get_display_date())
        if self.location:
            parts.append(self.location)
        return " - ".join(parts)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Race(name='{self.name}', date={self.date}, location='{self.location}')"
