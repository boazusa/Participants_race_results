"""
===============================================================================
Project: Running Records Analysis
Module: Race Result Model
Description: Data model for race results.
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
from datetime import datetime, date, time

from ..exceptions import DataValidationError
from ..utils.validation import validate_race_result_data
from ..utils.time_utils import parse_time_string, format_timedelta


@dataclass
class RaceResult:
    """
    Data model for a race result.
    """
    
    participant_name: str
    race_name: str
    race_date: Optional[date] = None
    position: Optional[int] = None
    time_str: Optional[str] = None
    time_seconds: Optional[float] = None
    category: Optional[str] = None
    age_group: Optional[str] = None
    gender: Optional[str] = None
    
    # Additional metadata
    race_location: Optional[str] = None
    race_url: Optional[str] = None
    bib_number: Optional[str] = None
    chip_time: Optional[str] = None
    gun_time: Optional[str] = None
    pace: Optional[str] = None
    status: Optional[str] = None  # Finished, DNF, DNS, etc.
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Normalize date
        if isinstance(self.race_date, str):
            try:
                self.race_date = datetime.strptime(self.race_date, "%Y-%m-%d").date()
            except ValueError:
                try:
                    self.race_date = datetime.strptime(self.race_date, "%d/%m/%Y").date()
                except ValueError:
                    self.race_date = None
        
        # Normalize strings
        self.participant_name = self.participant_name.strip() if self.participant_name else ""
        self.race_name = self.race_name.strip() if self.race_name else ""
        self.category = self.category.strip() if self.category else ""
        self.age_group = self.age_group.strip() if self.age_group else ""
        self.gender = self.gender.strip() if self.gender else ""
        
        # Parse time if provided
        if self.time_str and not self.time_seconds:
            self.time_seconds = self._parse_time_to_seconds(self.time_str)
    
    def _parse_time_to_seconds(self, time_str: str) -> Optional[float]:
        """
        Parse time string to seconds.
        
        Args:
            time_str: Time string (e.g., "45:30", "1:23:45")
            
        Returns:
            Time in seconds or None if parsing fails
        """
        try:
            return parse_time_string(time_str)
        except (ValueError, TypeError):
            return None
    
    def validate(self) -> Dict[str, List[str]]:
        """
        Validate race result data.
        
        Returns:
            Dictionary of validation errors
        """
        data = {
            "participant_name": self.participant_name,
            "race_name": self.race_name,
            "time_str": self.time_str,
            "position": self.position,
        }
        
        return validate_race_result_data(data)
    
    def is_valid(self) -> bool:
        """
        Check if race result data is valid.
        
        Returns:
            True if valid, False otherwise
        """
        errors = self.validate()
        return len(errors) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert race result to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "participant_name": self.participant_name,
            "race_name": self.race_name,
            "race_date": self.race_date.isoformat() if self.race_date else None,
            "position": self.position,
            "time_str": self.time_str,
            "time_seconds": self.time_seconds,
            "category": self.category,
            "age_group": self.age_group,
            "gender": self.gender,
            "race_location": self.race_location,
            "race_url": self.race_url,
            "bib_number": self.bib_number,
            "chip_time": self.chip_time,
            "gun_time": self.gun_time,
            "pace": self.pace,
            "status": self.status,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RaceResult":
        """
        Create race result from dictionary.
        
        Args:
            data: Dictionary with race result data
            
        Returns:
            RaceResult instance
        """
        return cls(
            participant_name=data.get("participant_name", ""),
            race_name=data.get("race_name", ""),
            race_date=data.get("race_date"),
            position=data.get("position"),
            time_str=data.get("time_str"),
            time_seconds=data.get("time_seconds"),
            category=data.get("category"),
            age_group=data.get("age_group"),
            gender=data.get("gender"),
            race_location=data.get("race_location"),
            race_url=data.get("race_url"),
            bib_number=data.get("bib_number"),
            chip_time=data.get("chip_time"),
            gun_time=data.get("gun_time"),
            pace=data.get("pace"),
            status=data.get("status"),
        )
    
    def get_display_time(self) -> str:
        """
        Get formatted time for display.
        
        Returns:
            Formatted time string
        """
        if self.time_str:
            return self.time_str
        elif self.time_seconds:
            return format_timedelta(self.time_seconds)
        return ""
    
    def get_display_position(self) -> str:
        """
        Get formatted position for display.
        
        Returns:
            Formatted position string
        """
        if self.position is None:
            return ""
        return str(self.position)
    
    def is_finished(self) -> bool:
        """
        Check if participant finished the race.
        
        Returns:
            True if finished, False otherwise
        """
        if self.status:
            return self.status.upper() == "FINISHED"
        return self.time_str is not None or self.time_seconds is not None
    
    def is_dnf(self) -> bool:
        """
        Check if participant did not finish.
        
        Returns:
            True if DNF, False otherwise
        """
        if self.status:
            return self.status.upper() == "DNF"
        return False
    
    def is_dns(self) -> bool:
        """
        Check if participant did not start.
        
        Returns:
            True if DNS, False otherwise
        """
        if self.status:
            return self.status.upper() == "DNS"
        return False
    
    def get_year(self) -> Optional[int]:
        """
        Get race year.
        
        Returns:
            Year as integer or None
        """
        return self.race_date.year if self.race_date else None
    
    def __str__(self) -> str:
        """String representation."""
        parts = [self.participant_name, self.race_name]
        if self.time_str:
            parts.append(self.time_str)
        if self.position:
            parts.append(f"#{self.position}")
        return " - ".join(parts)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"RaceResult(participant='{self.participant_name}', "
                f"race='{self.race_name}', time='{self.time_str}', "
                f"position={self.position})")
    
    def __lt__(self, other) -> bool:
        """
        Compare race results for sorting.
        Sorts by time (fastest first), then by position.
        """
        if not isinstance(other, RaceResult):
            return NotImplemented
        
        # Compare by time if both have time_seconds
        if self.time_seconds is not None and other.time_seconds is not None:
            return self.time_seconds < other.time_seconds
        
        # Compare by position if both have position
        if self.position is not None and other.position is not None:
            return self.position < other.position
        
        # If one has time and other doesn't, the one with time comes first
        if self.time_seconds is not None:
            return True
        if other.time_seconds is not None:
            return False
        
        # Finally, compare by position
        if self.position is not None:
            return True
        if other.position is not None:
            return False
        
        return False
