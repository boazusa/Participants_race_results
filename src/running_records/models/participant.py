"""
===============================================================================
Project: Running Records Analysis
Module: Participant Model
Description: Data model for race participants.
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
from typing import Optional, Dict, Any
from datetime import datetime

from ..exceptions import DataValidationError
from ..utils.validation import validate_participant_data
from ..utils.normalization import normalize_year, normalize_gender, normalize_distance, normalize_name


@dataclass
class Participant:
    """
    Data model for a race participant.
    """
    
    first_name: str
    last_name: str
    birth_year: Optional[int] = None
    gender: Optional[str] = None
    race_category: Optional[str] = None
    team: Optional[str] = None
    position: Optional[int] = None
    
    # Computed fields
    age: Optional[int] = field(init=False)
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Normalize data
        self.first_name = normalize_name(self.first_name) or ""
        self.last_name = normalize_name(self.last_name) or ""
        self.birth_year = normalize_year(self.birth_year)
        self.gender = normalize_gender(self.gender)
        self.race_category = normalize_distance(self.race_category) if self.race_category else None
        self.team = normalize_name(self.team)
        
        # Compute age
        if self.birth_year:
            self.age = datetime.now().year - self.birth_year
        else:
            self.age = None
    
    def validate(self) -> Dict[str, List[str]]:
        """
        Validate participant data.
        
        Returns:
            Dictionary of validation errors
        """
        data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "race_category": self.race_category,
        }
        
        return validate_participant_data(data)
    
    def is_valid(self) -> bool:
        """
        Check if participant data is valid.
        
        Returns:
            True if valid, False otherwise
        """
        errors = self.validate()
        return len(errors) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert participant to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "race_category": self.race_category,
            "team": self.team,
            "position": self.position,
            "age": self.age,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Participant":
        """
        Create participant from dictionary.
        
        Args:
            data: Dictionary with participant data
            
        Returns:
            Participant instance
        """
        return cls(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            birth_year=data.get("birth_year"),
            gender=data.get("gender"),
            race_category=data.get("race_category"),
            team=data.get("team"),
            position=data.get("position"),
        )
    
    @classmethod
    def from_dataframe_row(cls, row) -> "Participant":
        """
        Create participant from pandas DataFrame row.
        
        Args:
            row: Pandas Series or DataFrame row
            
        Returns:
            Participant instance
        """
        return cls(
            first_name=row.get("שם פרטי", ""),
            last_name=row.get("שם משפחה", ""),
            birth_year=row.get("שנת לידה"),
            gender=row.get("מגדר"),
            race_category=row.get("מקצה"),
            team=row.get("קבוצה"),
            position=row.get("מקום"),
        )
    
    def get_full_name(self) -> str:
        """
        Get participant's full name.
        
        Returns:
            Full name string
        """
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_display_name(self) -> str:
        """
        Get display name with title.
        
        Returns:
            Display name with gender title
        """
        full_name = self.get_full_name()
        if self.gender == "male":
            return f"Mr. {full_name}"
        elif self.gender == "female":
            return f"Ms. {full_name}"
        return full_name
    
    def __str__(self) -> str:
        """String representation."""
        return self.get_full_name()
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Participant(first_name='{self.first_name}', last_name='{self.last_name}', birth_year={self.birth_year}, gender='{self.gender}')"
