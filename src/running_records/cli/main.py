"""
===============================================================================
Project: Running Records Analysis
Module: CLI Main Entry Point
Description: Main command-line interface entry point.
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
from pathlib import Path

from .. import RaceAnalyzer, ScraperFactory
from ..config import config
from ..exceptions import RunningRecordsError
from .analyze import analyze
from .excel import excel


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config-file', '-c', type=click.Path(exists=True), 
              help='Path to configuration file')
@click.pass_context
def cli(ctx, verbose, config_file):
    """
    Running Records Analysis CLI
    
    A comprehensive tool for analyzing running race results from various websites.
    Supports scraping, filtering, analysis, and export functionality.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    # Load configuration if specified
    if config_file:
        try:
            config.load_from_file(config_file)
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            sys.exit(1)
    
    if verbose:
        click.echo(f"Running Records Analysis v{config.get_version()}")
        click.echo(f"Config loaded from: {config_file or 'default'}")


# Add subcommands
cli.add_command(analyze)
cli.add_command(excel)


@cli.command()
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
@click.pass_context
def analyze(ctx, url, race_name, output, years_back, min_age, max_age, gender, category):
    """
    Analyze race results from a given URL.
    
    This command scrapes participant data from the race URL, applies filters,
    computes best results, and exports to Excel.
    
    Example:
        running-records analyze https://regi.3plus.co.il/events/page/17492 --race-name "נס ציונה"
    """
    try:
        if ctx.obj['verbose']:
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
        
        if ctx.obj['verbose']:
            click.echo(f"Applying filters: {filters}")
        
        # Run analysis
        results = analyzer.analyze(**filters)
        
        if ctx.obj['verbose']:
            click.echo(f"Analysis complete. Results saved to: {results['output_file']}")
        else:
            click.echo(results['output_file'])
            
    except RunningRecordsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--race-name', '-n', help='Race name for output files')
@click.option('--output', '-o', help='Output directory (default: excel)')
@click.option('--years-back', '-y', type=int, default=5,
              help='Years to look back for best results (default: 5)')
@click.pass_context
def excel(ctx, input_file, race_name, output, years_back):
    """
    Analyze participants from an Excel file.
    
    This command reads participant data from an Excel file, fetches their best
    results from various websites, and exports to a new Excel file.
    
    Example:
        running-records excel participants.xlsx --race-name "My Race"
    """
    try:
        if ctx.obj['verbose']:
            click.echo(f"Analyzing Excel file: {input_file}")
        
        # Create analyzer for Excel input
        analyzer = RaceAnalyzer.from_excel(
            excel_path=input_file,
            race_name=race_name,
            output_dir=output or "excel"
        )
        
        # Run analysis
        results = analyzer.analyze(years_back=years_back)
        
        if ctx.obj['verbose']:
            click.echo(f"Analysis complete. Results saved to: {results['output_file']}")
        else:
            click.echo(results['output_file'])
            
    except RunningRecordsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('name')
@click.option('--years-back', '-y', type=int, default=5,
              help='Years to look back for results (default: 5)')
@click.option('--max-results', type=int, default=10,
              help='Maximum number of results to return (default: 10)')
@click.pass_context
def search(ctx, name, years_back, max_results):
    """
    Search for a person's race results.
    
    This command searches for race results for a specific person across
    various race websites.
    
    Example:
        running-records search "John Doe" --years-back 3
    """
    try:
        if ctx.obj['verbose']:
            click.echo(f"Searching for results: {name}")
        
        # Use ThreePlusScraper for search (it uses Shvoong)
        scraper = ScraperFactory.create_scraper("https://shvoong.co.il")
        results = scraper.search_person_results(name, years_back, max_results)
        
        if results:
            click.echo(f"Found {len(results)} results for {name}:")
            for i, result in enumerate(results[:max_results], 1):
                click.echo(f"{i}. {result['race_name']} - {result['time']} ({result['date']})")
        else:
            click.echo(f"No results found for {name}")
            
    except RunningRecordsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def config_show(ctx):
    """Show current configuration."""
    try:
        config_dict = config.to_dict()
        
        click.echo("Current Configuration:")
        click.echo("=" * 40)
        
        for section, values in config_dict.items():
            click.echo(f"\n[{section}]")
            for key, value in values.items():
                if isinstance(value, (list, dict)):
                    click.echo(f"  {key}: {type(value).__name__}")
                else:
                    click.echo(f"  {key}: {value}")
                    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('url')
@click.pass_context
def test_scraper(ctx, url):
    """Test scraper functionality for a given URL."""
    try:
        if ctx.obj['verbose']:
            click.echo(f"Testing scraper for: {url}")
        
        # Create appropriate scraper
        scraper = ScraperFactory.create_scraper(url)
        
        # Test participant scraping
        participants = scraper.scrape_participants()
        click.echo(f"Found {len(participants)} participants")
        
        # Show first few participants
        for i, participant in enumerate(participants[:3], 1):
            click.echo(f"  {i}. {participant}")
            
    except RunningRecordsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
