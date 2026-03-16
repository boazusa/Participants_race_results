#!/usr/bin/env python3
"""
Build script for creating development executable of the Flask race results app
Shows console window for debugging and easy stopping
"""

import PyInstaller.__main__

# PyInstaller configuration for Flask app (development version with console)
args = [
    'flask_app.py',
    '--onefile',           # Create single executable
    '--console',           # Show console window for debugging
    '--name=RaceResultsAppDev',  # Name the executable
    '--add-data=templates;templates',  # Include templates folder
    '--add-data=static;static',        # Include static folder if exists
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
]

PyInstaller.__main__.run(args)

print("Development executable created successfully!")
print("Find it in the 'dist' folder")
print("This version shows console window for easy stopping")
print("Press Ctrl+C in console to stop the app")
