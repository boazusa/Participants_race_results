#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Single Person Results Analyzer
Description: Fetches and processes individual race results from race results websites.
             Provides detailed analysis of a single participant's race history.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 15/11/2025
Last Modified: 24/11/2025
Version: 1.0.0
Python Version: 3.8+
Dependencies:
    - requests >= 2.26.0
    - beautifulsoup4 >= 4.10.0
    - pandas >= 1.3.0
    - numpy >= 1.21.0
License: [boazusa@hotmail.com]
===============================================================================
"""

import os
import sys

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from backend.raceview_api import RaceViewAPI, RaceViewEngine
import configparser

# BASE_DIR = os.path.dirname(__file__)  # backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

CONFIG_PATH = os.path.join(PROJECT_ROOT, "login_info", "login.ini")

config = configparser.ConfigParser()
files = config.read(CONFIG_PATH, encoding="utf-8")

if not files:
    raise FileNotFoundError(f"Could not read config: {CONFIG_PATH}")

EMAIL = config["login"]["email"]
PASSWORD = config["login"]["password"]
API_KEY = config["login"]["api_key"]

# Configure UTF-8 encoding for Windows console
if sys.platform == "win32":
    import locale
    # Set console to UTF-8 encoding
    try:
        os.system("chcp 65001 > nul")
    except:
        pass

def safe_print(*args, **kwargs):
    """Print function that handles Unicode encoding on Windows"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: replace problematic characters
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Replace emojis with text alternatives
                safe_arg = arg.replace("🔍", "Search:")
                safe_arg = safe_arg.replace("⚠️", "Warning:")
                safe_arg = safe_arg.replace("❌", "Error:")
                safe_arg = safe_arg.replace("✅", "Success:")
                safe_arg = safe_arg.replace("🎉", "Celebration:")
                safe_arg = safe_arg.replace("📊", "Data:")
                safe_arg = safe_arg.replace("🚀", "Launch:")
                safe_arg = safe_arg.replace("🎯", "Target:")
                safe_args.append(safe_arg)
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)


def fetch_and_process_results(first_name, last_name):

    # ==================================
    # Get results from RaceView
    # ==================================

    api = RaceViewAPI(
        email=EMAIL,
        password=PASSWORD,
        api_key=API_KEY
    )

    api.login()

    engine = RaceViewEngine(api)

    full_name = f"{first_name} {last_name}"

    results = engine.get_runner_results(full_name)

    if not results:
        raise ValueError(f"No results found for {full_name}")

    df = pd.json_normalize(results)

    safe_print(f"✅ Found {len(df)} race results")

    # ==================================
    # Normalize distance
    # ==================================

    def normalize_distance(distance):

        if pd.isna(distance):
            return np.nan

        tolerance = 200

        distance_map = {
            5000: "5K",
            10000: "10K",
            15000: "15K",
            21000: "21K",
            42195: "42K"
        }

        for target, name in distance_map.items():
            if abs(distance - target) <= tolerance:
                return name

        return np.nan

    df["normalized_distance"] = (
        df["distance"]
        .apply(normalize_distance)
    )

    # ==================================
    # Best available time
    # ==================================

    df["best_time"] = (
        pd.to_numeric(
            df["personal_time"],
            errors="coerce"
        )
        .fillna(
            pd.to_numeric(
                df["result"],
                errors="coerce"
            )
        )
    )

    df = df[df["best_time"].notna()]

    df["race_time"] = pd.to_timedelta(
        df["best_time"],
        unit="s"
    )

    # ==================================
    # Best result per distance
    # ==================================

    df_best = df[
        df["normalized_distance"].notna()
    ].copy()

    best_indices = (
        df_best
        .groupby("normalized_distance")["race_time"]
        .idxmin()
    )

    best_rows = df.loc[best_indices].copy()

    best_rows["הערה"] = "Best Result"

    # ==================================
    # Sort
    # ==================================

    order = ["42K", "21K", "15K", "10K", "5K"]

    best_rows["order_key"] = (
        best_rows["normalized_distance"]
        .apply(
            lambda x:
            order.index(x)
            if x in order
            else len(order)
        )
    )

    best_rows = (
        best_rows
        .sort_values("order_key")
        .drop(columns="order_key")
    )

    # ==================================
    # Export
    # ==================================

    excel_dir = "excel"

    os.makedirs(
        excel_dir,
        exist_ok=True
    )

    output_file = (
        f"excel/{first_name}_{last_name}_תוצאות_ריצה.xlsx"
    )

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        best_rows.to_excel(
            writer,
            index=False,
            sheet_name="Sheet1",
            startrow=0
        )

        start_row = len(best_rows) + 3

        df.to_excel(
            writer,
            index=False,
            sheet_name="Sheet1",
            startrow=start_row
        )

    safe_print(f"✅ Saved to {output_file}")

    return best_rows, df


if __name__ == "__main__":
    best, all_results = fetch_and_process_results("בועז", "בילגורי")

    print(best)
    print(all_results)


# TODO
# Flask app that shows best results and all results
# import to excel best result of a list of names and provide best results for specific category

"""
    def normalize_distance(value):
        if pd.isna(value) or str(value).strip() == "":
            return np.nan
        s = str(value).strip()
        if s in ['10 ק"מ', '10ק"מ', "9800", "10000", "10 קמ"]:
            return "10K"
        if s in ["21097", "21000", "21K", "21k"]:
            return "21K"
        if s in ["42195", "42K", "42k"]:
            return "42K"
        if "15" in s:
            return "15K"
        if "5" in s and "2" not in s:
            return "5K"
        return np.nan
"""