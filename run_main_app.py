#!/usr/bin/env python3
"""
Entry point for the main Flask application.
This script runs the main race results analyzer web app.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web.main_app import app

if __name__ == "__main__":
    app.run(debug=True)
