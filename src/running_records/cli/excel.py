"""
===============================================================================
Project: Running Records Analysis
Module: CLI Excel Commands
Description: CLI commands for Excel processing operations.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
===============================================================================
"""

import click
import sys
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

from .. import RaceAnalyzer, ExcelExporter
from ..exceptions import RunningRecordsError


@click.group()
def excel():
    """Commands for Excel processing operations."""
    pass


@excel.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--sheet-name', '-s', help='Sheet name to read (default: first sheet)')
@click.option('--output', '-o', help='Output Excel file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def validate(input_file, sheet_name, output, verbose):
    """
    Validate Excel file structure and content.
    
    This command checks if the Excel file has the expected structure for
    participant data and reports any issues found.
    
    Example:
        running-records excel validate participants.xlsx
    """
    try:
        if verbose:
            click.echo(f"Validating Excel file: {input_file}")
        
        # Read Excel file
        if sheet_name:
            df = pd.read_excel(input_file, sheet_name=sheet_name)
        else:
            df = pd.read_excel(input_file)
        
        if verbose:
            click.echo(f"Found {len(df)} rows and {len(df.columns)} columns")
            click.echo(f"Columns: {list(df.columns)}")
        
        # Validate structure
        issues = []
        
        # Check required columns
        required_columns = ['name']  # At minimum, need name column
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            issues.append(f"Missing required columns: {missing_columns}")
        
        # Check for empty data
        if df.empty:
            issues.append("Excel file is empty")
        
        # Check for empty names
        if 'name' in df.columns:
            empty_names = df['name'].isna().sum()
            if empty_names > 0:
                issues.append(f"{empty_names} rows have empty names")
        
        # Report results
        if issues:
            click.echo("Validation issues found:")
            for issue in issues:
                click.echo(f"  - {issue}")
            sys.exit(1)
        else:
            click.echo("✓ Excel file structure is valid")
            
    except Exception as e:
        click.echo(f"Error validating Excel file: {e}", err=True)
        sys.exit(1)


@excel.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--race-name', '-n', help='Race name for output files')
@click.option('--output', '-o', help='Output directory (default: excel)')
@click.option('--years-back', '-y', type=int, default=5,
              help='Years to look back for best results (default: 5)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def analyze(input_file, race_name, output, years_back, verbose):
    """
    Analyze participants from an Excel file.
    
    This command reads participant data from an Excel file, fetches their best
    results from various websites, and exports to a new Excel file.
    
    Example:
        running-records excel analyze participants.xlsx --race-name "My Race"
    """
    try:
        if verbose:
            click.echo(f"Analyzing Excel file: {input_file}")
        
        # Create analyzer for Excel input
        analyzer = RaceAnalyzer.from_excel(
            excel_path=input_file,
            race_name=race_name,
            output_dir=output or "excel"
        )
        
        # Run analysis
        results = analyzer.analyze(years_back=years_back)
        
        if verbose:
            click.echo(f"Analysis complete. Results saved to: {results['output_file']}")
            click.echo(f"Total participants: {results['total_participants']}")
            click.echo(f"Best results found: {results['best_results_count']}")
        else:
            click.echo(results['output_file'])
            
    except RunningRecordsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@excel.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output Excel file path')
@click.option('--sheet-name', '-s', default='Summary',
              help='Sheet name for summary (default: Summary)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def summary(input_file, output, sheet_name, verbose):
    """
    Generate summary statistics for Excel file.
    
    This command analyzes the participant data in an Excel file and creates
    a summary with statistics about age groups, genders, etc.
    
    Example:
        running-records excel summary participants.xlsx
    """
    try:
        if verbose:
            click.echo(f"Generating summary for: {input_file}")
        
        # Read Excel file
        df = pd.read_excel(input_file)
        
        if verbose:
            click.echo(f"Processing {len(df)} participants")
        
        # Generate summary statistics
        summary_data = {
            'Total Participants': [len(df)],
            'Unique Names': [df['name'].nunique()] if 'name' in df.columns else ['N/A'],
        }
        
        # Age statistics
        if 'birth_year' in df.columns:
            current_year = pd.Timestamp.now().year
            df['age'] = current_year - df['birth_year']
            summary_data['Average Age'] = [df['age'].mean()]
            summary_data['Min Age'] = [df['age'].min()]
            summary_data['Max Age'] = [df['age'].max()]
        
        # Gender statistics
        if 'gender' in df.columns:
            gender_counts = df['gender'].value_counts()
            for gender, count in gender_counts.items():
                summary_data[f'Gender - {gender}'] = [count]
        
        # Create summary DataFrame
        summary_df = pd.DataFrame(summary_data)
        
        # Determine output path
        if output:
            output_path = output
        else:
            input_path = Path(input_file)
            output_path = input_path.parent / f"{input_path.stem}_summary.xlsx"
        
        # Write to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Also include original data
            df.to_excel(writer, sheet_name='Original Data', index=False)
        
        if verbose:
            click.echo(f"Summary saved to: {output_path}")
            click.echo(f"Summary statistics:")
            for stat, value in summary_data.items():
                click.echo(f"  {stat}: {value[0]}")
        else:
            click.echo(output_path)
            
    except Exception as e:
        click.echo(f"Error generating summary: {e}", err=True)
        sys.exit(1)


@excel.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--column', '-c', help='Column name to filter on')
@click.option('--value', help='Value to filter for')
@click.option('--output', '-o', help='Output Excel file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def filter(input_file, column, value, output, verbose):
    """
    Filter Excel file based on column values.
    
    This command filters rows in an Excel file based on a column value
    and saves the filtered results to a new file.
    
    Example:
        running-records excel filter participants.xlsx --column gender --value male
    """
    try:
        if not column or not value:
            click.echo("Error: Both --column and --value are required", err=True)
            sys.exit(1)
        
        if verbose:
            click.echo(f"Filtering {input_file} where {column} = {value}")
        
        # Read Excel file
        df = pd.read_excel(input_file)
        
        if column not in df.columns:
            click.echo(f"Error: Column '{column}' not found in Excel file", err=True)
            sys.exit(1)
        
        # Apply filter
        filtered_df = df[df[column] == value]
        
        if verbose:
            click.echo(f"Filtered {len(filtered_df)} rows from {len(df)} total rows")
        
        if filtered_df.empty:
            click.echo("No rows match the filter criteria")
            sys.exit(0)
        
        # Determine output path
        if output:
            output_path = output
        else:
            input_path = Path(input_file)
            output_path = input_path.parent / f"{input_path.stem}_filtered_{column}_{value}.xlsx"
        
        # Write filtered data
        filtered_df.to_excel(output_path, index=False)
        
        if verbose:
            click.echo(f"Filtered data saved to: {output_path}")
        else:
            click.echo(output_path)
            
    except Exception as e:
        click.echo(f"Error filtering Excel file: {e}", err=True)
        sys.exit(1)


@excel.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output Excel file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def deduplicate(input_file, output, verbose):
    """
    Remove duplicate participants from Excel file.
    
    This command removes duplicate rows based on participant name and
    saves the deduplicated data to a new file.
    
    Example:
        running-records excel deduplicate participants.xlsx
    """
    try:
        if verbose:
            click.echo(f"Deduplicating {input_file}")
        
        # Read Excel file
        df = pd.read_excel(input_file)
        
        if verbose:
            click.echo(f"Original rows: {len(df)}")
        
        # Check for name column
        if 'name' not in df.columns:
            click.echo("Error: 'name' column not found in Excel file", err=True)
            sys.exit(1)
        
        # Remove duplicates based on name
        deduplicated_df = df.drop_duplicates(subset=['name'], keep='first')
        
        duplicates_removed = len(df) - len(deduplicated_df)
        
        if verbose:
            click.echo(f"Duplicates removed: {duplicates_removed}")
            click.echo(f"Deduplicated rows: {len(deduplicated_df)}")
        
        # Determine output path
        if output:
            output_path = output
        else:
            input_path = Path(input_file)
            output_path = input_path.parent / f"{input_path.stem}_deduplicated.xlsx"
        
        # Write deduplicated data
        deduplicated_df.to_excel(output_path, index=False)
        
        if verbose:
            click.echo(f"Deduplicated data saved to: {output_path}")
        else:
            click.echo(output_path)
            
    except Exception as e:
        click.echo(f"Error deduplicating Excel file: {e}", err=True)
        sys.exit(1)
