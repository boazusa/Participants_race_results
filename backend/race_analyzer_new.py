#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Best Race Results Analyzer
Description: Core logic for scraping race participants and computing best race results per participant.
             Handles data extraction, processing, and analysis of race results.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 15/11/2025
Last Modified: 04/03/2025
Version: 1.0.1
Python Version: 3.8+
Dependencies:
    - pandas >= 1.3.0
    - requests >= 2.26.0
    - beautifulsoup4 >= 4.10.0
    - numpy >= 1.21.0
    - openpyxl >= 3.0.0
Performance: Network-bound; performance depends on external sites and number of participants.
License: [boazusa@hotmail.com]
===============================================================================
"""

import os
import configparser
import sys
from datetime import datetime
from pandas.io.sql import partial
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from urllib.parse import quote
from requests.exceptions import RequestException, Timeout
# from raceview_api import RaceViewAPI
from backend.raceview_api import RaceViewAPI, RaceViewEngine

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


def format_seconds(value):
    if pd.isna(value) or value == "":
        return ""

    # אם כבר בפורמט זמן
    if isinstance(value, str) and ":" in value:
        return value

    try:
        seconds = float(value)
    except:
        return ""

    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)

    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


class best_race_results_per_participant:
    def __init__(self, url, race_name=None, excel_path=None, years_back=5):
        """
        :param url:
        :param excel_path:
        Parameters:
        - self.url: the page URL containing the participants table
        - self.excel_path: path to Excel or CSV file
        """
        self.url = url.replace("view-source:", "")
        self.excel_path = excel_path
        self.participants_table_df = None
        self.names_list = None
        self.race_name = race_name
        self.output_file = ""
        self.participants_table_df = None
        self.years_back = years_back

        # Create excel directory if it doesn't exist
        excel_dir = "excel"
        if not os.path.exists(excel_dir):
            os.makedirs(excel_dir, exist_ok=True)

        api = RaceViewAPI(
            email=EMAIL,
            password=PASSWORD,
            api_key=API_KEY
        )

        # Login פעם אחת בלבד
        api.login()

        self.engine = RaceViewEngine(api)

    @staticmethod
    def normalize_year(y):
        """Normalize 'שנת לידה' to an integer year."""
        if pd.isna(y):
            return None
        if isinstance(y, int):
            return y
        if isinstance(y, float):
            return int(y)
        if isinstance(y, str):
            y = y.strip()  # Ensure leading/trailing spaces are removed
            if "/" in y:
                parts = y.split("/")
                try:
                    if len(parts) >= 3:
                        year = int(parts[2])
                    elif len(parts) == 2:
                        year = int(parts[1])  # e.g., MM/YYYY
                    elif len(parts) == 1:
                        year = int(parts[0])  # e.g., YYYY
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

    # 3plus event only
    def scrape_3plus_participants_table(self):
        """
        Scrape a participants table from a given URL and return as a pandas DataFrame.
        Sorts by 'תוצאה מיטבית' if it exists.
        :return:
        - df: pandas DataFrame containing the table
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36 "
        }

        # Fetch the page
        response = requests.get(self.url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the participants table - try both 3plus and Ashkelon table IDs
        table = soup.find("table", id="m_ph4wp1_tblData")  # 3plus
        if not table:
            table = soup.find("table", id="m_ph3wp1_tblData")  # Ashkelon
        if not table:
            raise ValueError("Participants table not found in the HTML source.")

        # Extract headers
        table_headers = [th.get_text(strip=True) for th in table.find_all("th")]

        # Extract rows
        rows = []
        for tr in table.find("tbody").find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            rows.append(cells)

        # Create DataFrame
        df = pd.DataFrame(rows, columns=table_headers)

        print(f"Found {len(df)} participants registered to this race.")

        return df

    def scrape_realtiming_participants_table(self, drop_first_col=True):
        """
        Scrape the participants table from a RealTiming event page and return it as a pandas DataFrame.

        self.url : str
            The event page URL (e.g. https://www.realtiming.co.il/events/1242/list)
        self.excel_path : str, optional
            Path to save the resulting DataFrame as an Excel file.
        Parameters:
        ----------
        drop_first_col : bool, optional
            If True, removes the first column (often just a running index).

        Returns:
        -------
        pandas.DataFrame
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/119.0.0.0 Safari/537.36"
            )
        }

        # Request page content
        response = requests.get(self.url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the main results table
        table = soup.find("table")
        if not table:
            raise ValueError("❌ No table found on the given URL.")

        # Extract headers
        headers_row = [
            th.get_text(strip=True) for th in table.find("thead").find_all("th")
        ]

        # Extract data rows
        rows = []
        for tr in table.find("tbody").find_all("tr"):
            row = [td.get_text(strip=True) for td in tr.find_all("td")]
            rows.append(row)

        # Build DataFrame
        df = pd.DataFrame(rows, columns=headers_row)

        if "מין" in df.columns:
            df = df.rename(columns={"מין": "מגדר"})

        # Normalize gender column
        for gender_col in ["מגדר", "מין"]:
            if gender_col in df.columns:
                df[gender_col] = (
                    df[gender_col].replace({"ז": "male", "נ": "female"}).str.strip()
                )

        # Drop the first column if requested
        if drop_first_col and df.shape[1] > 0:
            df = df.iloc[:, 1:]

        print(f"Found {len(df)} participants registered to this race.")

        return df

    def scrape_modiin_participants_table(self):
        # Get the HTML
        response = requests.get(self.url)
        response.encoding = "utf-8"  # ensure Hebrew text is read properly
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all table rows
        rows = []
        for tr in soup.find_all("tr"):
            cells = [
                td.get_text(strip=True).replace("\xa0", " ") for td in tr.find_all("td")
            ]
            if cells:
                rows.append(cells)

        # Convert to DataFrame
        df = pd.DataFrame(
            rows, columns=["שם פרטי", "שם משפחה", "שנת לידה", "מגדר", "מקצה", "קבוצה"]
        )

        # Normalize gender column
        for gender_col in ["מגדר", "מין"]:
            if gender_col in df.columns:
                df[gender_col] = (
                    df[gender_col]
                    .replace({"זכר": "male", "נקבה": "female"})
                    .str.strip()
                )

        print(f"Found {len(df)} participants registered to this race.")

        return df

    def scrape_participants_table(self):
        url_lower = self.url.lower()
        if "realtiming.co.il" in url_lower:
            df = self.scrape_realtiming_participants_table()
        elif "3plus.co.il" in url_lower or "shvoong" in url_lower or "ashkelon.runisrael.org.il" in url_lower:
            df = self.scrape_3plus_participants_table()
        elif "modiin" in url_lower:
            df = self.scrape_modiin_participants_table()
        else:
            raise ValueError("Unknown event URL")

        self.participants_table_df = df
        return df

    def get_filtered_names_3plus_realtiming(
        self, min_year=None, max_year=None, gender=None, race_keyword=None
    ):
        """
        Returns a list of (first_name, last_name) tuples filtered by year of birth, gender, and race.

        Parameters:
        - :param min_year: include participants with year of birth >= min_year
        - :param max_year: include participants with year of birth <= max_year
        - :param gender: filter by 'male' or 'female', or 'ז' / 'נ'
        - :param race_keyword: substring to search for in the 'מקצה' column (e.g., "10", "5", "2")

        :return:
        - List of tuples: [(first_name, last_name), ...]
        """
        # Read Excel file
        df = self.participants_table_df.copy()
        df["שנת לידה"] = df["שנת לידה"].apply(self.normalize_year)

        # Apply filters
        if min_year is not None:
            df = df[df["שנת לידה"] >= min_year]
        if max_year is not None:
            df = df[df["שנת לידה"] <= max_year]
        if gender is not None:
            df = df[df["מגדר"] == gender]
        if race_keyword is not None:
            # First try direct contains
            mask = (
                df["מקצה"].astype(str).str.contains(race_keyword, case=False, na=False)
            )

            # Also check normalized distance if no matches found
            if not mask.any() and race_keyword in ["5K", "10K", "15K", "21K", "42K"]:
                normalized_race = race_keyword
                mask = (
                    df["מקצה"].apply(lambda x: str(self.normalize_distance(str(x))))
                    == normalized_race
                )

            df = df[mask]

        # Build list of tuples
        self.names_list = list(
            df[["שם פרטי", "שם משפחה"]].itertuples(index=False, name=None)
        )
        return self.names_list

    def get_filtered_names_shvoong(
        self, min_year=1976, max_year=1985, gender="male", race_keyword=None
    ):
        """
        Returns a list of (first_name, last_name) tuples filtered by year of birth, gender, and race.

        Parameters:
        - :param race_keyword: substring to search for in the 'מקצה' column (e.g., "10", "5", "2")

        :return:
        - List of tuples: [(first_name, last_name), ...]
        """
        # Read Excel file
        df = self.participants_table_df.copy()
        # df['שנת לידה'] = df['שנת לידה'].apply(self.normalize_year)

        # Apply filters
        if race_keyword is not None:
            # Normalize the race keyword if it's a standard race category
            if race_keyword in ["5K", "10K", "15K", "21K", "42K"]:
                mask = (
                    df["מקצה"].apply(lambda x: str(self.normalize_distance(str(x))))
                    == race_keyword
                )
            else:
                # Try direct contains for non-standard race categories
                mask = (
                    df["מקצה"]
                    .astype(str)
                    .str.contains(race_keyword, case=False, na=False)
                )

            df = df[mask]

        # Build list of tuples
        if len(df) > 0:
            self.names_list = list(
                df[["שם פרטי", "שם משפחה"]].itertuples(index=False, name=None)
            )
        else:
            self.names_list = []

        return self.names_list

    def get_filtered_names(
        self, min_year=1976, max_year=1985, gender="male", race_keyword=None
    ):
        url_lower = self.url.lower()

        # Remember the filter years so we can reflect the age range in the output filename later
        self.min_year_param = min_year
        self.max_year_param = max_year

        if "realtiming.co.il" in url_lower:
            return self.get_filtered_names_3plus_realtiming(
                min_year=min_year,
                max_year=max_year,
                gender=gender,
                race_keyword=race_keyword,
            )
        elif "3plus.co.il" in url_lower or "modiin" in url_lower or "ashkelon.runisrael.org.il" in url_lower:
            return self.get_filtered_names_3plus_realtiming(
                min_year=min_year,
                max_year=max_year,
                gender=gender,
                race_keyword=race_keyword,
            )
        elif "shvoong" in url_lower:
            if "21" in race_keyword:
                race_keyword = "חצי מרתון"
            return self.get_filtered_names_shvoong(
                min_year=min_year,
                max_year=max_year,
                gender=gender,
                race_keyword=race_keyword,
            )

    @staticmethod
    def normalize_distance(value):
        if pd.isna(value) or str(value).strip() == "":
            return np.nan
        s = str(value).strip()
        # if s in ["10 ק\"מ", "10ק\"מ", "9800", "10000", "10 קמ", "10 km - competitive"]:
        if s in ['10 ק"מ', '10ק"מ', "9800", "10000", "10 קמ"]:
            return "10K"
        # if s in ["21097", "21000", "21K", "21k"]:
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
        ]:
            return "21K"
        if s in ["42195", "42K", "42k"]:
            return "42K"
        if "15" in s:
            return "15K"
        if "5" in s and "2" not in s:
            return "5K"
        return np.nan

    @staticmethod
    def choose_best_time_string(row):
        """
        Return the best valid time string between זמן אישי and תוצאה
        """
        for col in ["זמן אישי", "תוצאה"]:
            val = str(row.get(col, "")).strip()
            if val not in ["00:00:00", "0", "", "NaT", "None"]:
                return val
        return ""

    
    def fetch_best_result(self, first_name, last_name, category, years_back=5):

        full_name = f"{first_name} {last_name}"

        results = self.engine.get_runner_results(full_name)
        if not results:
            return None

        # df = pd.DataFrame(results)
        df = pd.json_normalize(results)

        df = self.engine.filter_by_years(df, years_back)
        df = self.engine.filter_by_distance(df, category)

        best = self.engine.pick_best_result(df)
        if best is None:
            return None

        best["שם פרטי"] = first_name
        best["שם משפחה"] = last_name
        # best["תוצאה מיטבית"] = str(pd.to_timedelta(best["best_time"], unit="s"))
        best["תוצאה מיטבית"] = format_seconds(best["best_time"])
        print(f"==================== Best result for {first_name} {last_name}: {best['תוצאה מיטבית']}")
        best["הערה"] = "Best Result"

        return best
    
    # def fetch_best_result(
    #         self,
    #         first_name,
    #         last_name,
    #         category,
    #         timeout_seconds=10,
    #         years_back=5
    # ):
    #     try:
    #         full_name = f"{first_name} {last_name}"

    #         # if full_name in self.runner_cache:
    #         #     results_json = self.runner_cache[full_name]
    #         # else:
    #         #     results_json = self.raceview_api.search_runner(full_name)
    #         #     self.runner_cache[full_name] = results_json

    #         results_json = self.raceview_api.search_runner(full_name)

    #         if not results_json:
    #             return None

    #         results = results_json.get("data", {}).get("results", [])

    #         if not results:
    #             safe_print(f"⚠️ No results for {full_name}")
    #             return None

    #         df = pd.DataFrame(results)

    #         if df.empty:
    #             return None

    #         # ----------------------------
    #         # Date filter
    #         # ----------------------------
    #         current_year = datetime.now().year
    #         min_year = current_year - years_back

    #         df["date"] = pd.to_datetime(df["date"], errors="coerce")

    #         df = df[
    #             (df["date"].dt.year >= min_year) &
    #             (df["date"].dt.year <= current_year)
    #         ]

    #         if df.empty:
    #             safe_print(
    #                 f"⚠️ No results for {full_name} in last {years_back} years"
    #             )
    #             return None

    #         # ----------------------------
    #         # Distance filter
    #         # ----------------------------
    #         distance_map = {
    #             "5K": 5000,
    #             "10K": 10000,
    #             "15K": 15000,
    #             "21K": 21000,
    #             "42K": 42195
    #         }

    #         target_distance = distance_map.get(category)

    #         if target_distance is None:
    #             safe_print(f"⚠️ Unknown category {category}")
    #             return None

    #         # ירושלים מחזיר 21000 במקום 21097
    #         tolerance = 200

    #         df = df[
    #             (df["distance"] >= target_distance - tolerance) &
    #             (df["distance"] <= target_distance + tolerance)
    #         ]

    #         if df.empty:
    #             safe_print(
    #                 f"⚠️ No {category} results for {full_name}"
    #             )
    #             return None

    #         # ----------------------------
    #         # Choose best time
    #         # ----------------------------
    #         df["best_time"] = (
    #             pd.to_numeric(df["personal_time"], errors="coerce")
    #             .fillna(
    #                 pd.to_numeric(df["result"], errors="coerce")
    #             )
    #         )

    #         df = df[df["best_time"].notna()]

    #         if df.empty:
    #             return None

    #         best_row = df.loc[df["best_time"].idxmin()].copy()

    #         # ----------------------------
    #         # Match old SHVOONG columns
    #         # ----------------------------
    #         best_row["שם פרטי"] = first_name
    #         best_row["שם משפחה"] = last_name

    #         best_row["תוצאה מיטבית"] = str(
    #             pd.to_timedelta(best_row["best_time"], unit="s")
    #         )

    #         best_row["מרוץ"] = best_row.get("event_name")
    #         best_row["מקצה"] = best_row.get("race_name")

    #         best_row["race_time"] = pd.to_timedelta(
    #             best_row["best_time"],
    #             unit="s"
    #         )

    #         best_row["הערה"] = "Best Result"

    #         return best_row

    #     except Exception as e:
    #         safe_print(
    #             f"❌ Error fetching {first_name} {last_name}: {e}"
    #         )
    #         return None

    def best_results_for_category(self, category):
        best_results = []

        for first_name, last_name in self.names_list:
            best_row = self.fetch_best_result(first_name, last_name, category, years_back=self.years_back)
            if best_row is not None:
                best_results.append(best_row)

        if not best_results:
            safe_print("❌ No best results found for any person")
            return

        df_best = pd.DataFrame(best_results)
        df_best.reset_index(drop=True, inplace=True)

        # תוצאה מיטבית sorting step
        df_best["race_time"] = pd.to_timedelta(df_best["תוצאה מיטבית"], errors="coerce")
        df_best = df_best.sort_values(by="race_time", ascending=True)

        # Only save to Excel if excel_path is provided
        if self.excel_path:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

            # Derive age range suffix from stored min/max years (if available), e.g. _20-55
            age_suffix = ""
            min_year = getattr(self, "min_year_param", None)
            max_year = getattr(self, "max_year_param", None)
            if min_year is not None and max_year is not None:
                current_year = datetime.now().year
                youngest_age = current_year - max_year  # higher birth year -> younger
                oldest_age = current_year - min_year  # lower birth year -> older
                age_suffix = f"_{youngest_age}-{oldest_age}"

            output_file = f"excel/{timestamp}_{self.race_name}_best_results_{category}{age_suffix}.xlsx"
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                df_best.to_excel(writer, index=False)
            print(f"Saved best results for category '{category}' to {output_file}")

        return df_best


if __name__ == "__main__":
    # Example usage

    # race = "לוד"
    # event_url = "https://regi.3plus.co.il/events/page/17381"  # Lod, 3plus

    # race = "באר יעקב"
    # event_url = "https://regi.3plus.co.il/events/page/17401"  # Be'er Ya'akov, 3plus

    # race = "מכבים"
    # event_url = "https://www.matnasmodiin.org.il/html5/UAPI.TAF?get=209"  # מכבים

    race = "קיסריה"
    event_url = "view-source:https://regi.shvoong.co.il/shvoong/page/17720"

    # race = "בית שמש"
    # event_url = "view-source:https://www.realtiming.co.il/events/1242/list"  # Beit Shmesh, Realtiming

    test = best_race_results_per_participant(event_url, race_name=race, excel_path=None)

    df_participants = test.scrape_participants_table()
    print(df_participants.head(10))

    names_filtered = test.get_filtered_names(
        min_year=1970, max_year=2005, gender="male", race_keyword="21"
    )
    print(f"names_list_filtered = {names_filtered}")

    race_category = "21K"  # Could be "42K", "21K", "15K", "10K", "5K", To find best result in a category
    test.best_results_for_category(race_category)

"""
1) participants_3plus.py
2) list_from_table.py
3) best_results_for_people_list.py
"""

"""
    # # For analyzing realtiming event
    # df_participants = test.scrape_realtiming_participants_table()
    # 
    # # For analyzing 3plus event
    # df_participants = test.scrape_3plus_participants_table()
"""
