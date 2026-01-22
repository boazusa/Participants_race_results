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

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def fetch_and_process_results(first_name, last_name):
    # === STEP 1: Fetch data from website ===
    from urllib.parse import quote
    query = quote(f"{first_name} {last_name}")
    url = f"https://raceresults.shvoong.co.il/race-result/?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/141.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    if not table:
        raise ValueError("❌ No table found on page")

    # --- Extract headers ---
    thead = table.find("thead")
    headers = [th.get_text(strip=True) for th in thead.find_all("th")]

    # --- Extract rows ---
    tbody = table.find("tbody")
    rows = []
    for tr in tbody.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if cells:
            rows.append(cells)

    # --- Normalize columns ---
    max_cols = max(len(r) for r in rows)
    headers = headers[:max_cols]
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    # --- Create DataFrame ---
    df = pd.DataFrame(rows, columns=headers)
    print(f"✅ Extracted {len(df)} rows, {len(df.columns)} columns")

    # === STEP 2: Normalize & compute best results ===

    def normalize_distance(value):
        if pd.isna(value) or str(value).strip() == "":
            return np.nan
        s = str(value).strip()
        if s in ["10 ק\"מ", "10ק\"מ", "9800", "10000", "10 קמ"]:
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

    df["normalized_distance"] = df["מקצה"].apply(normalize_distance)

    def parse_time(row):
        try:
            time_str = row["זמן אישי"]
            if time_str in ["00:00:00", "0", "", None, np.nan]:
                time_str = row["תוצאה"]
            return pd.to_timedelta(time_str)
        except Exception:
            return pd.NaT

    df["race_time"] = df.apply(parse_time, axis=1)

    # --- Select valid distances for best results ---
    df_for_best = df[
        df["normalized_distance"].notna() &
        (~df["normalized_distance"].isin(["30000", "7000"]))
    ]

    # --- Get best result (min time) per distance ---
    best_indices = df_for_best.groupby("normalized_distance")["race_time"].idxmin()
    best_rows = df.loc[best_indices].copy()
    best_rows["הערה"] = "Best Result"

    # --- Order best results: 42K → 21K → 15K → 10K → 5K ---
    order = ["42K", "21K", "15K", "10K", "5K"]
    best_rows["order_key"] = best_rows["normalized_distance"].apply(
        lambda x: order.index(x) if x in order else len(order)
    )
    best_rows = best_rows.sort_values("order_key").drop(columns="order_key")

    # === STEP 3: Export to Excel ===
    excel_dir = "excel"
    if not os.path.exists(excel_dir):
        os.makedirs(excel_dir, exist_ok=True)
    output_file = f"excel/{first_name}_{last_name}_תוצאות_ריצה.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        # Write best results (with headers)
        best_rows.to_excel(writer, index=False, sheet_name="Sheet1", startrow=0)
        # Leave 2 empty lines, then write raw results (with headers)
        start_row = len(best_rows) + 3
        df.to_excel(writer, index=False, sheet_name="Sheet1", startrow=start_row)

    print(f"✅ Saved to {output_file}")
    print("✅ Ordered best results: 42K → 21K → 15K → 10K → 5K")

    return best_rows, df  # Optional: return the dataframes for inspection

if __name__ == "__main__":
    best, all_results = fetch_and_process_results("בועז", "בילגורי")

    print(best)
    print(all_results)


# TODO
# Flask app that shows best results and all results
# import to excel best result of a list of names and provide best results for specific category
