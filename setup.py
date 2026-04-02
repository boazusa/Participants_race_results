"""
===============================================================================
Project: Running Records Analysis
Module: Setup Script
Description: Setup script for installing the running_records package.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 03/04/2026
Version: 2.0.0
Python Version: 3.9+
License: [boazusa@hotmail.com]
===============================================================================
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="running-records",
    version="2.0.0",
    author="Boaz Bilgory",
    author_email="boazusa@hotmail.com",
    description="A comprehensive system for analyzing running race results",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boazbilgory/running-records",
    project_urls={
        "Bug Tracker": "https://github.com/boazbilgory/running-records/issues",
        "Documentation": "https://github.com/boazbilgory/running-records/wiki",
        "Source Code": "https://github.com/boazbilgory/running-records",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.4.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "running-records=running_records.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "running_records": [
            "config/*.yaml",
            "templates/*.html",
            "static/*",
        ],
    },
    zip_safe=False,
    keywords="running, race results, analysis, scraping, web",
)
