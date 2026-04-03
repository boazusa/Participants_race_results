"""
===============================================================================
Project: Running Records Analysis
Module: CLI Analyze Commands
Description: CLI commands for race analysis operations.
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
from typing import Dict, Any, Optional

from .. import RaceAnalyzer
from ..exceptions import RunningRecordsError


@click.group()
def analyze():
    """Commands for race analysis operations."""
    pass


@analyze.command()
@click.argument('url')
@click.option('--race-name', '-n', help='Race name for output files')
@click.option('--output', '-o', help='Output directory (default: excel)')
@click.option('--years-back', '-y', type=int, default=5,
              help='Years to look back for best results (default: 5)')
@click.option('--min-age', type=int, help='Minimum age filter')
@click.option('--max-age', type=int, help='Maximum age filter')
@click.option('--gender', type=click.Choice(['male', 'female', 'both']),
              default='both', help='Gender filter')
@click.option('--category', help='Race category/distance filter')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def race(url, race_name, output, years_back, min_age, max_age, gender, category, verbose):
    """
    Analyze race results from a given URL.
    
    This command scrapes participant data from the race URL, applies filters,
    computes best results, and exports to Excel.
    
    Example:
        running-records analyze race https://regi.3plus.co.il/events/page/17492 --race-name "נס ציונה"
    """
    try:
        if verbose:
            click.echo(f"Analyzing race: {url}")
        
        # Create analyzer
        analyzer = RaceAnalyzer(
            url=url,
            race_name=race_name,
            output_dir=output or "excel"
        )
        
        # Set filters
        filters = {}
        if min_age is not None:
            filters['min_year'] = min_age
        if max_age is not None:
            filters['max_year'] = max_age
        if gender != 'both':
            filters['gender'] = gender
        if category:
            filters['race_keyword'] = category
        filters['years_back'] = years_back
        
        if verbose:
            click.echo(f"Applying filters: {filters}")
        
        # Run analysis
        results = analyzer.analyze(**filters)
        
        if verbose:
            click.echo(f"Analysis complete. Results saved to: {results['output_file']}")
            click.echo(f"Total participants: {results['total_participants']}")
            click.echo(f"Filtered participants: {results['filtered_participants']}")
            click.echo(f"Best results found: {results['best_results_count']}")
        else:
            click.echo(results['output_file'])
            
    except RunningRecordsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@analyze.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--race-name', '-n', help='Race name for output files')
@click.option('--output', '-o', help='Output directory (default: excel)')
@click.option('--years-back', '-y', type=int, default=5,
              help='Years to look back for best results (default: 5)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def excel(input_file, race_name, output, years_back, verbose):
    """
    Analyze participants from an Excel file.
    
    This command reads participant data from an Excel file, fetches their best
    results from various websites, and exports to a new Excel file.
    
    Example:
        running-records analyze excel participants.xlsx --race-name "My Race"
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


@analyze.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--output-dir', '-o', help='Output directory (default: excel)')
@click.option('--years-back', '-y', type=int, default=5,
              help='Years to look back for best results (default: 5)')
@click.option('--min-age', type=int, help='Minimum age filter')
@click.option('--max-age', type=int, help='Maximum age filter')
@click.option('--gender', type=click.Choice(['male', 'female', 'both']),
              default='both', help='Gender filter')
@click.option('--category', help='Race category/distance filter')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def batch(urls, output_dir, years_back, min_age, max_age, gender, category, verbose):
    """
    Analyze multiple races in batch.
    
    This command processes multiple race URLs and generates separate Excel files
    for each race with the same filter criteria applied.
    
    Example:
        running-records analyze batch url1 url2 url3 --category "10K"
    """
    try:
        if verbose:
            click.echo(f"Analyzing {len(urls)} races in batch")
        
        results = []
        
        for i, url in enumerate(urls, 1):
            if verbose:
                click.echo(f"Processing race {i}/{len(urls)}: {url}")
            
            try:
                # Create analyzer for this race
                analyzer = RaceAnalyzer(
                    url=url,
                    output_dir=output_dir or "excel"
                )
                
                # Set filters
                filters = {}
                if min_age is not None:
                    filters['min_year'] = min_age
                if max_age is not None:
                    filters['max_year'] = max_age
                if gender != 'both':
                    filters['gender'] = gender
                if category:
                    filters['race_keyword'] = category
                filters['years_back'] = years_back
                
                # Run analysis
                result = analyzer.analyze(**filters)
                results.append(result)
                
                if verbose:
                    click.echo(f"  ✓ Complete: {result['output_file']}")
                    
            except Exception as e:
                if verbose:
                    click.echo(f"  ✗ Failed: {e}")
                continue
        
        # Summary
        click.echo(f"\nBatch analysis complete:")
        click.echo(f"  Total URLs: {len(urls)}")
        click.echo(f"  Successful: {len(results)}")
        click.echo(f"  Failed: {len(urls) - len(results)}")
        
        if results:
            click.echo(f"\nGenerated files:")
            for result in results:
                click.echo(f"  - {result['output_file']}")
            
    except KeyboardInterrupt:
        click.echo("\nBatch analysis interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)
