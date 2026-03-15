#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone Script: Best Race Results from Excel Sheet
Description: Reads participants from Excel, filters by criteria, fetches best results from shvoong.co.il, and saves to Excel.
Author: Based on original by Boaz Bilgory
Dependencies: pandas, requests, beautifulsoup4, openpyxl
"""

import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote
from requests.exceptions import RequestException, Timeout


class BestResultsFromExcel:
    def __init__(self, excel_input_path, race_name=None, output_excel_path=None):
        self.excel_input_path = excel_input_path
        self.race_name = race_name or "Race"
        self.output_excel_path = output_excel_path
        self.participants_df = None
        self.filtered_names = None

        # Create output directory if needed
        if self.output_excel_path:
            output_dir = os.path.dirname(self.output_excel_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

    @staticmethod
    def normalize_year(y):
        """Normalize birth year to integer."""
        if pd.isna(y):
            return None
        if isinstance(y, (int, float)):
            return int(y)
        if isinstance(y, str):
            y = y.strip()
            if "/" in y:
                parts = y.split("/")
                try:
                    if len(parts) >= 3:
                        year = int(parts[2])
                    elif len(parts) == 2:
                        year = int(parts[1])
                    elif len(parts) == 1:
                        year = int(parts[0])
                    else:
                        return None
                    if year < 100:
                        year += 1900 if year > 25 else 2000
                    return year
                except (ValueError, TypeError):
                    return None
            try:
                return int(y)
            except (ValueError, TypeError):
                return None
        return None

    @staticmethod
    def normalize_distance(value):
        if pd.isna(value) or str(value).strip() == "":
            return pd.NA
        s = str(value).strip()
        if s in ['10 ק"מ', '10ק"מ', "9800", "10000", "10 קמ"]:
            return "10K"
        if s in [
            "21097",
            '21 ק"מ',
            "21000",
            "21K",
            "21k",
            "חצי מרתון",
            "חצי מרתון תחרותי",
            "חצי-מרתון",
            "חצי_מרתון",
            "Half Marathon",
        ]:  # Added "Half Marathon"
            return "21K"
        if s in ["42195", "42K", "42k"]:
            return "42K"
        if "15" in s:
            return "15K"
        if "5" in s and "2" not in s:
            return "5K"
        return pd.NA

    @staticmethod
    def choose_best_time_string(row):
        """Return the best valid time string."""
        for col in ["זמן אישי", "תוצאה"]:
            val = str(row.get(col, "")).strip()
            if val not in ["00:00:00", "0", "", "NaT", "None"]:
                return val
        return ""

    def load_participants_from_excel(self):
        """Load and preprocess participants from Excel."""
        df = pd.read_excel(self.excel_input_path)
        # print("Original columns:", df.columns.tolist())  # Debug: check actual columns

        # Rename columns (use actual names from print above)
        df = df.rename(
            columns={
                "שם": "name",  # Assuming 'שם' is the name column; adjust if different
                "מגדר": "מגדר",
                "שנת לידה": "שנת לידה",
                "מקצה": "מקצה",
                "מועדון": "מועדון",
                "מדינה": "מדינה",
            }
        )
        # print("After rename:", df.columns.tolist())  # Debug

        # Split 'name' into first and last (assuming space-separated full name)
        if "name" in df.columns:
            df[["שם פרטי", "שם משפחה"]] = df["name"].str.split(" ", n=1, expand=True)
            df = df.drop(columns=["name"])
        else:
            print("❌ 'name' column not found after rename. Check column names.")
            return None

        # Normalize gender
        # print("Gender before replace:", df['מגדר'].head())  # Debug
        df["מגדר"] = (
            df["מגדר"]
            .astype(str)
            .str.strip()
            .replace(
                {
                    "ז": "male",
                    "נ": "female",
                    "זכר": "male",
                    "נקבה": "female",
                    "m": "male",
                    "f": "female",
                    "M": "male",
                    "F": "female",  # Added uppercase
                }
            )
            .str.lower()
        )
        # print("Gender after replace:", df['מגדר'].head())  # Debug

        # print("Sample data:\n", df.head())  # Debug: check processed data
        self.participants_df = df
        print(f"✅ Loaded {len(df)} participants from Excel.")
        return df

    def filter_participants(
        self, min_year=None, max_year=None, gender=None, race_keyword=None
    ):
        """Filter participants based on criteria."""
        if self.participants_df is None:
            self.load_participants_from_excel()

        df = self.participants_df.copy()
        df["שנת לידה"] = df["שנת לידה"].apply(self.normalize_year)
        # print(f"Birth years after normalize: {df['שנת לידה'].unique()}")  # Debug

        if min_year is not None:
            before = len(df)
            df = df[df["שנת לידה"] >= min_year]
            print(f"After min_year {min_year}: {len(df)} (was {before})")
        if max_year is not None:
            before = len(df)
            df = df[df["שנת לידה"] <= max_year]
            print(f"After max_year {max_year}: {len(df)} (was {before})")
        if gender is not None:
            before = len(df)
            df = df[df["מגדר"] == gender.lower()]
            print(f"After gender {gender}: {len(df)} (was {before})")
        if race_keyword is not None:
            before = len(df)
            mask = (
                df["מקצה"].astype(str).str.contains(race_keyword, case=False, na=False)
            )
            if not mask.any() and race_keyword in [
                "5K",
                "10K",
                "15K",
                "Half Marathon",
                "21K",
                "42K",
            ]:  # Added '21'
                if race_keyword == "21" or race_keyword == "Half Marathon":
                    mask = (
                        df["מקצה"].apply(lambda x: str(self.normalize_distance(str(x))))
                        == "21K"
                    )
                else:
                    mask = (
                        df["מקצה"].apply(lambda x: str(self.normalize_distance(str(x))))
                        == race_keyword
                    )
            df = df[mask]
            print(f"After race_keyword {race_keyword}: {len(df)} (was {before})")

        self.filtered_names = list(
            df[["שם פרטי", "שם משפחה"]].itertuples(index=False, name=None)
        )
        # print(f"Filtered names sample: {self.filtered_names[:5]}")  # Debug
        print(f"✅ Filtered to {len(self.filtered_names)} participants.")
        return self.filtered_names

    def fetch_best_result(self, first_name, last_name, category, timeout_seconds=10):
        """Fetch best result for a participant from shvoong.co.il."""
        query = quote(f"{first_name} {last_name}")
        url = f"https://raceresults.shvoong.co.il/race-result/?q={query}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=timeout_seconds)
            response.raise_for_status()
        except Timeout:
            print(f"⏰ Timeout for {first_name} {last_name}")
            return None
        except RequestException as e:
            print(f"❌ Request failed for {first_name} {last_name}: {e}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            print(f"❌ No table found for {first_name} {last_name}")
            return None

        thead = table.find("thead")
        headers = [th.get_text(strip=True) for th in thead.find_all("th")]
        tbody = table.find("tbody")

        rows = []
        for tr in tbody.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cells:
                rows.append(cells)

        if not rows:
            print(f"❌ No results for {first_name} {last_name}")
            return None

        max_cols = max(len(r) for r in rows)
        headers = headers[:max_cols]
        rows = [r + [""] * (max_cols - len(r)) for r in rows]

        df = pd.DataFrame(rows, columns=headers)
        df["normalized_distance"] = df["מקצה"].apply(self.normalize_distance)
        df["תוצאה מיטבית"] = df.apply(self.choose_best_time_string, axis=1)
        df["race_time"] = pd.to_timedelta(df["תוצאה מיטבית"], errors="coerce")

        df_cat = df[df["normalized_distance"] == category]
        if df_cat.empty:
            print(f"⚠️ No results for {first_name} {last_name} in {category}")
            return None

        best_idx = df_cat["race_time"].idxmin()
        best_row = df_cat.loc[best_idx].copy()
        best_row["שם פרטי"] = first_name
        best_row["שם משפחה"] = last_name
        best_row["הערה"] = "Best Result"

        return best_row

    def get_best_results_for_category(self, category):
        """Get best results for all filtered participants in the category."""
        if not self.filtered_names:
            print("❌ No filtered names available. Run filter_participants() first.")
            return None

        best_results = []
        for first_name, last_name in self.filtered_names:
            result = self.fetch_best_result(first_name, last_name, category)
            if result is not None:
                best_results.append(result)

        if not best_results:
            print("❌ No best results found.")
            return None

        df_best = pd.DataFrame(best_results)
        df_best["race_time"] = pd.to_timedelta(df_best["תוצאה מיטבית"], errors="coerce")
        df_best = df_best.sort_values(by="race_time")

        if self.output_excel_path:
            with pd.ExcelWriter(self.output_excel_path, engine="openpyxl") as writer:
                df_best.to_excel(writer, index=False)
            print(f"✅ Saved best results to {self.output_excel_path}")

        return df_best


if __name__ == "__main__":
    # Example usage
    excel_input = r"C:\Users\USER\Documents\Python\running_records\running_records_windsurf\excel\מרתון_ירושלים_חצי_מרתון_45_49.xlsx"  # Replace with your Excel path
    output_excel = r"C:\Users\USER\Documents\Python\running_records\running_records_windsurf\excel\מרתון_ירושלים_חצי_מרתון_45_49_output.xlsx"  # Optional output path

    processor = BestResultsFromExcel(
        excel_input_path=excel_input,
        race_name="Your Race",
        output_excel_path=output_excel,
    )

    # Filter participants (adjust parameters as needed)
    # filtered = processor.filter_participants(min_year=1970, max_year=2005, gender='male', race_keyword='21')
    filtered = processor.filter_participants(
        min_year=1970, max_year=2005, gender="male", race_keyword="21K"
    )  # Changed to '21K'

    # Get best results for category
    category = "21K"
    results = processor.get_best_results_for_category(category)

    if results is not None:
        print(results.head())
