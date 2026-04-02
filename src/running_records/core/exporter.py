"""
===============================================================================
Project: Running Records Analysis
Module: Excel Exporter
Description: Excel file export functionality for race results.
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
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from ..config import config
from ..exceptions import ExcelExportError, ExportError
from ..utils.file_utils import ensure_directory, safe_filename, generate_excel_filename


class ExcelExporter:
    """
    Handles exporting race results to Excel files.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the Excel exporter.
        
        Args:
            output_dir: Directory for output files (uses config default if None)
        """
        self.output_dir = Path(output_dir or config.excel.output_dir)
        ensure_directory(self.output_dir)
    
    def export_results(
        self,
        results_df: pd.DataFrame,
        file_path: str,
        race_name: Optional[str] = None,
        category: Optional[str] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Export race results to Excel file.
        
        Args:
            results_df: DataFrame containing race results
            file_path: Path for output file
            race_name: Name of the race (for metadata)
            category: Race category (for metadata)
            include_metadata: Whether to include metadata sheet
            
        Returns:
            Path to generated Excel file
            
        Raises:
            ExcelExportError: If export fails
        """
        try:
            if results_df.empty:
                raise ExcelExportError("No data to export", file_path, "xlsx")
            
            # Ensure file path is safe
            file_path = safe_filename(file_path)
            full_path = self.output_dir / file_path
            
            # Ensure directory exists
            ensure_directory(full_path.parent)
            
            # Create Excel writer
            with pd.ExcelWriter(
                full_path,
                engine='openpyxl',
                mode='w'
            ) as writer:
                # Write results data
                self._write_results_sheet(writer, results_df, category)
                
                # Write metadata if requested
                if include_metadata:
                    self._write_metadata_sheet(
                        writer, 
                        race_name, 
                        category, 
                        len(results_df)
                    )
            
            return str(full_path)
            
        except Exception as e:
            if isinstance(e, (ExcelExportError, ExportError)):
                raise
            raise ExcelExportError(f"Failed to export Excel file: {str(e)}", file_path, "xlsx")
    
    def export_participants(
        self,
        participants_df: pd.DataFrame,
        file_path: str,
        race_name: Optional[str] = None
    ) -> str:
        """
        Export participants data to Excel file.
        
        Args:
            participants_df: DataFrame containing participants data
            file_path: Path for output file
            race_name: Name of the race
            
        Returns:
            Path to generated Excel file
        """
        try:
            if participants_df.empty:
                raise ExcelExportError("No participant data to export", file_path, "xlsx")
            
            # Ensure file path is safe
            file_path = safe_filename(file_path)
            full_path = self.output_dir / file_path
            
            # Ensure directory exists
            ensure_directory(full_path.parent)
            
            # Create Excel writer
            with pd.ExcelWriter(
                full_path,
                engine='openpyxl',
                mode='w'
            ) as writer:
                # Write participants data
                participants_df.to_excel(
                    writer,
                    sheet_name='Participants',
                    index=False
                )
                
                # Write metadata
                self._write_participants_metadata_sheet(
                    writer,
                    race_name,
                    len(participants_df)
                )
            
            return str(full_path)
            
        except Exception as e:
            if isinstance(e, (ExcelExportError, ExportError)):
                raise
            raise ExcelExportError(f"Failed to export participants Excel file: {str(e)}", file_path, "xlsx")
    
    def generate_filename(
        self,
        race_name: str,
        category: str,
        age_range: str,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate standardized filename for Excel export.
        
        Args:
            race_name: Name of the race
            category: Race category
            age_range: Age range (e.g., "40-49")
            timestamp: Optional timestamp (defaults to current time)
            
        Returns:
            Generated filename
        """
        return generate_excel_filename(race_name, category, age_range, timestamp)
    
    def _write_results_sheet(
        self,
        writer: pd.ExcelWriter,
        results_df: pd.DataFrame,
        category: Optional[str] = None
    ) -> None:
        """
        Write the main results sheet.
        
        Args:
            writer: Excel writer object
            results_df: Results DataFrame
            category: Race category
        """
        # Prepare data for export
        export_df = results_df.copy()
        
        # Define column order and names
        column_order = [
            'שם מרוץ',
            'שם פרטי',
            'שם משפחה',
            'תאריך אירוע',
            'תוצאה מיטבית',
            'קטגוריה',
            'מיקום כללי',
            'מיקום בקבוצה'
        ]
        
        # Filter to available columns
        available_columns = [col for col in column_order if col in export_df.columns]
        
        if available_columns:
            export_df = export_df[available_columns]
        
        # Write to Excel
        export_df.to_excel(
            writer,
            sheet_name='Results',
            index=False
        )
        
        # Get worksheet for formatting
        worksheet = writer.sheets['Results']
        
        # Auto-adjust column widths
        self._auto_adjust_column_widths(worksheet, export_df)
        
        # Add filters
        if len(export_df) > 0:
            worksheet.auto_filter.ref = f"A1:{worksheet.dimensions.split(':')[1]}"
    
    def _write_metadata_sheet(
        self,
        writer: pd.ExcelWriter,
        race_name: Optional[str],
        category: Optional[str],
        total_results: int
    ) -> None:
        """
        Write metadata sheet with export information.
        
        Args:
            writer: Excel writer object
            race_name: Race name
            category: Race category
            total_results: Number of results
        """
        metadata = [
            ['Export Information', ''],
            ['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Race Name', race_name or 'Unknown'],
            ['Category', category or 'Unknown'],
            ['Total Results', total_results],
            ['', ''],
            ['Data Source', 'Running Records Analysis'],
            ['Version', '2.0.0'],
            ['Author', 'Boaz Bilgory'],
        ]
        
        metadata_df = pd.DataFrame(metadata, columns=['Property', 'Value'])
        
        metadata_df.to_excel(
            writer,
            sheet_name='Metadata',
            index=False
        )
    
    def _write_participants_metadata_sheet(
        self,
        writer: pd.ExcelWriter,
        race_name: Optional[str],
        total_participants: int
    ) -> None:
        """
        Write metadata sheet for participants export.
        
        Args:
            writer: Excel writer object
            race_name: Race name
            total_participants: Number of participants
        """
        metadata = [
            ['Export Information', ''],
            ['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Race Name', race_name or 'Unknown'],
            ['Total Participants', total_participants],
            ['', ''],
            ['Data Source', 'Running Records Analysis'],
            ['Version', '2.0.0'],
            ['Author', 'Boaz Bilgory'],
        ]
        
        metadata_df = pd.DataFrame(metadata, columns=['Property', 'Value'])
        
        metadata_df.to_excel(
            writer,
            sheet_name='Metadata',
            index=False
        )
    
    def _auto_adjust_column_widths(self, worksheet, df: pd.DataFrame) -> None:
        """
        Auto-adjust column widths based on content.
        
        Args:
            worksheet: Excel worksheet object
            df: DataFrame with data
        """
        try:
            from openpyxl.utils import get_column_letter
            
            for idx, col in enumerate(df.columns, 1):
                column_letter = get_column_letter(idx)
                
                # Find maximum length in column
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                )
                
                # Set column width (with some padding)
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
        except ImportError:
            # openpyxl not available or version issue
            pass
        except Exception:
            # Any other error, ignore width adjustment
            pass
    
    def create_summary_report(
        self,
        results_df: pd.DataFrame,
        race_name: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Create summary statistics for the results.
        
        Args:
            results_df: Results DataFrame
            race_name: Race name
            category: Race category
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'race_name': race_name,
            'category': category,
            'total_participants': len(results_df),
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        if not results_df.empty and 'תוצאה מיטבית' in results_df.columns:
            # Time statistics
            try:
                from ..utils.time_utils import parse_time_string
                
                times = []
                for time_str in results_df['תוצאה מיטבית']:
                    td = parse_time_string(time_str)
                    if td:
                        times.append(td.total_seconds())
                
                if times:
                    summary.update({
                        'fastest_time': min(times),
                        'slowest_time': max(times),
                        'average_time': sum(times) / len(times),
                        'time_std': pd.Series(times).std(),
                    })
                    
            except Exception:
                pass  # Ignore time calculation errors
        
        return summary
