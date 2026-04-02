"""
===============================================================================
Project: Running Records Analysis
Module: Participant Filter
Description: Filtering logic for race participants.
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
from typing import List, Tuple, Optional
from datetime import datetime

from ..exceptions import FilterError
from ..utils.normalization import normalize_year, normalize_distance, normalize_gender


class ParticipantFilter:
    """
    Handles filtering of race participants based on various criteria.
    """
    
    def filter_participants(
        self,
        participants_df: pd.DataFrame,
        min_year: int,
        max_year: int,
        gender: Optional[str] = None,
        race_keyword: Optional[str] = None
    ) -> List[Tuple[str, str]]:
        """
        Filter participants based on birth year, gender, and race category.
        
        Args:
            participants_df: DataFrame containing participants data
            min_year: Minimum birth year (inclusive)
            max_year: Maximum birth year (inclusive)
            gender: Gender filter ('male' or 'female')
            race_keyword: Keyword to filter race categories
            
        Returns:
            List of (first_name, last_name) tuples
            
        Raises:
            FilterError: If filtering fails
        """
        if participants_df is None or participants_df.empty:
            return []
        
        try:
            # Make a copy to avoid modifying original
            df = participants_df.copy()
            
            # Normalize birth years
            if 'שנת לידה' in df.columns:
                df['שנת לידה'] = df['שנת לידה'].apply(normalize_year)
                
                # Filter by birth year range
                df = df[
                    (df['שנת לידה'] >= min_year) & 
                    (df['שנת לידה'] <= max_year)
                ]
            
            # Filter by gender
            if gender and 'מגדר' in df.columns:
                normalized_gender = normalize_gender(gender)
                if normalized_gender:
                    df = df[df['מגדר'] == normalized_gender]
            
            # Filter by race keyword
            if race_keyword and 'מקצה' in df.columns:
                # Normalize distances for filtering
                df['מקצה_נורמל'] = df['מקצה'].apply(normalize_distance)
                
                # Create search mask
                if not pd.isna(df['מקצה_נורמל']).all():
                    # Try exact match first
                    mask = df['מקצה_נורמל'] == race_keyword
                    
                    # If no exact matches, try partial match
                    if not mask.any():
                        mask = df['מקצה'].astype(str).str.contains(
                            str(race_keyword), 
                            case=False, 
                            na=False
                        )
                    
                    df = df[mask]
                else:
                    # Fallback to string search
                    mask = df['מקצה'].astype(str).str.contains(
                        str(race_keyword), 
                        case=False, 
                        na=False
                    )
                    df = df[mask]
            
            # Extract names
            if 'שם פרטי' in df.columns and 'שם משפחה' in df.columns:
                # Remove rows with missing names
                df = df[df['שם פרטי'].notna() & df['שם משפחה'].notna()]
                df = df[df['שם פרטי'] != ''] & (df['שם משפחה'] != '')
                
                # Convert to list of tuples
                names_list = [
                    (str(row['שם פרטי']).strip(), str(row['שם משפחה']).strip())
                    for _, row in df.iterrows()
                ]
                
                return names_list
            
            return []
            
        except Exception as e:
            raise FilterError(f"Failed to filter participants: {str(e)}")
    
    def get_filter_statistics(
        self,
        participants_df: pd.DataFrame,
        min_year: int,
        max_year: int,
        gender: Optional[str] = None,
        race_keyword: Optional[str] = None
    ) -> dict:
        """
        Get statistics about filtering results.
        
        Args:
            participants_df: DataFrame containing participants data
            min_year: Minimum birth year
            max_year: Maximum birth year
            gender: Gender filter
            race_keyword: Race keyword filter
            
        Returns:
            Dictionary with filter statistics
        """
        stats = {
            'total_participants': len(participants_df) if participants_df is not None else 0,
            'age_filtered': 0,
            'gender_filtered': 0,
            'race_filtered': 0,
            'final_count': 0,
            'age_range': f"{min_year}-{max_year}",
        }
        
        if participants_df is None or participants_df.empty:
            return stats
        
        try:
            df = participants_df.copy()
            
            # Age filtering
            if 'שנת לידה' in df.columns:
                df['שנת לידה'] = df['שנת לידה'].apply(normalize_year)
                age_mask = (df['שנת לידה'] >= min_year) & (df['שנת לידה'] <= max_year)
                df = df[age_mask]
                stats['age_filtered'] = len(df)
            
            # Gender filtering
            if gender and 'מגדר' in df.columns:
                normalized_gender = normalize_gender(gender)
                if normalized_gender:
                    gender_mask = df['מגדר'] == normalized_gender
                    df = df[gender_mask]
                    stats['gender_filtered'] = len(df)
            
            # Race filtering
            if race_keyword and 'מקצה' in df.columns:
                df['מקצה_נורמל'] = df['מקצה'].apply(normalize_distance)
                
                if not pd.isna(df['מקצה_נורמל']).all():
                    race_mask = df['מקצה_נורמל'] == race_keyword
                    if not race_mask.any():
                        race_mask = df['מקצה'].astype(str).str.contains(
                            str(race_keyword), case=False, na=False
                        )
                    df = df[race_mask]
                else:
                    race_mask = df['מקצה'].astype(str).str.contains(
                        str(race_keyword), case=False, na=False
                    )
                    df = df[race_mask]
                
                stats['race_filtered'] = len(df)
            
            # Final count (with valid names)
            if 'שם פרטי' in df.columns and 'שם משפחה' in df.columns:
                df = df[df['שם פרטי'].notna() & df['שם משפחה'].notna()]
                df = df[df['שם פרטי'] != ''] & (df['שם משפחה'] != '')
                stats['final_count'] = len(df)
            
        except Exception:
            pass  # Return default stats on error
        
        return stats
    
    def get_age_distribution(self, participants_df: pd.DataFrame) -> dict:
        """
        Get age distribution of participants.
        
        Args:
            participants_df: DataFrame containing participants data
            
        Returns:
            Dictionary with age distribution statistics
        """
        if participants_df is None or 'שנת לידה' not in participants_df.columns:
            return {}
        
        try:
            df = participants_df.copy()
            df['שנת לידה'] = df['שנת לידה'].apply(normalize_year)
            df = df[df['שנת לידה'].notna()]
            
            current_year = datetime.now().year
            df['age'] = current_year - df['שנת לידה']
            
            # Age ranges
            age_ranges = {
                '0-19': (0, 19),
                '20-29': (20, 29),
                '30-39': (30, 39),
                '40-49': (40, 49),
                '50-59': (50, 59),
                '60-69': (60, 69),
                '70+': (70, 150)
            }
            
            distribution = {}
            for range_name, (min_age, max_age) in age_ranges.items():
                count = len(df[(df['age'] >= min_age) & (df['age'] <= max_age)])
                distribution[range_name] = count
            
            # Add overall statistics
            distribution['total'] = len(df)
            distribution['average_age'] = df['age'].mean() if len(df) > 0 else 0
            distribution['min_age'] = df['age'].min() if len(df) > 0 else 0
            distribution['max_age'] = df['age'].max() if len(df) > 0 else 0
            
            return distribution
            
        except Exception:
            return {}
    
    def get_gender_distribution(self, participants_df: pd.DataFrame) -> dict:
        """
        Get gender distribution of participants.
        
        Args:
            participants_df: DataFrame containing participants data
            
        Returns:
            Dictionary with gender distribution statistics
        """
        if participants_df is None or 'מגדר' not in participants_df.columns:
            return {}
        
        try:
            df = participants_df.copy()
            df = df[df['מגדר'].notna()]
            
            # Normalize genders
            df['מגדר_נורמל'] = df['מגדר'].apply(normalize_gender)
            df = df[df['מגדר_נורמל'].notna()]
            
            distribution = {
                'male': len(df[df['מגדר_נורמל'] == 'male']),
                'female': len(df[df['מגדר_נורמל'] == 'female']),
                'total': len(df)
            }
            
            return distribution
            
        except Exception:
            return {}
    
    def get_race_category_distribution(self, participants_df: pd.DataFrame) -> dict:
        """
        Get distribution of race categories.
        
        Args:
            participants_df: DataFrame containing participants data
            
        Returns:
            Dictionary with race category distribution
        """
        if participants_df is None or 'מקצה' not in participants_df.columns:
            return {}
        
        try:
            df = participants_df.copy()
            df = df[df['מקצה'].notna()]
            
            # Normalize distances
            df['מקצה_נורמל'] = df['מקצה'].apply(normalize_distance)
            
            # Count by normalized category
            normalized_counts = df['מקקצה_נורמל'].value_counts().to_dict()
            
            # Also count by original category for reference
            original_counts = df['מקצה'].value_counts().to_dict()
            
            return {
                'normalized': normalized_counts,
                'original': original_counts,
                'total': len(df)
            }
            
        except Exception:
            return {}
