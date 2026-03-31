#!/usr/bin/env python3
"""
Build script for creating optimized executable of the Flask race results app
"""

import PyInstaller.__main__
import os

# Get the parent directory (project root)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
flask_app_path = os.path.join(project_root, 'flask_app.py')
templates_path = os.path.join(project_root, 'templates')
static_path = os.path.join(project_root, 'static')

# PyInstaller configuration for Flask app (optimized for size)
args = [
    flask_app_path,
    '--onefile',           # Create single executable
    '--windowed',          # Hide console window
    '--name=RaceResultsAppOptimized',  # Name the executable
    f'--add-data={templates_path};templates',  # Include templates folder
    f'--add-data={static_path};static',        # Include static folder if exists
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
    '--hidden-import=best_results_3plus_or_realtiming_race',
    '--hidden-import=pytz',              # pandas needs pytz for timezone handling
    '--exclude-module=tkinter',        # Exclude GUI toolkit
    '--exclude-module=matplotlib',     # Exclude plotting (not used)
    '--exclude-module=PIL',            # Exclude image processing
    '--exclude-module=IPython',        # Exclude IPython
    '--exclude-module=jupyter',        # Exclude Jupyter
    '--exclude-module=notebook',       # Exclude notebook
    '--exclude-module=pytest',         # Exclude testing framework
    '--exclude-module=sphinx',         # Exclude documentation
    '--exclude-module=docutils',       # Exclude documentation tools
    '--exclude-module=pygments',       # Exclude syntax highlighting
    '--exclude-module=scipy',           # Exclude scipy (not used)
    '--exclude-module=sklearn',         # Exclude sklearn (not used)
    '--exclude-module=seaborn',         # Exclude seaborn (not used)
    '--exclude-module=nose',            # Exclude nose testing
    '--clean',               # Clean temporary files
    '--noconfirm',           # Don't ask for confirmation
    '--distpath', os.path.join(project_root, 'dist'),  # Output to parent dist folder
]

PyInstaller.__main__.run(args)

print("Optimized executable created successfully!")
print(f"Find it in: {os.path.join(project_root, 'dist')}")
print("Size should be smaller now!")
