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
Last Modified: 24/11/2025
Version: 1.0.0
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
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from urllib.parse import quote
from requests.exceptions import RequestException, Timeout


class best_race_results_per_participant:
    def __init__(self, url, race_name=None, excel_path=None):
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

        # Create excel directory if it doesn't exist
        excel_dir = "excel"
        if not os.path.exists(excel_dir):
            os.makedirs(excel_dir, exist_ok=True)

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
            if '/' in y:  # date format
                parts = y.split('/')
                year = int(parts[2])
                if year < 100:
                    year += 1900 if year > 25 else 2000
                return year
            try:
                return int(y)
            except (ValueError, TypeError):
                return None
        if isinstance(y, pd.Timestamp):
            return y.year
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

        # Find the participants table
        table = soup.find("table", id="m_ph4wp1_tblData")
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

        print(f"✅✅✅ Found {len(df)} participants registered to this race. ✅✅✅")

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
        headers_row = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]

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
        for gender_col in ['מגדר', 'מין']:
            if gender_col in df.columns:
                df[gender_col] = (
                    df[gender_col].replace({'ז': 'male', 'נ': 'female'}).str.strip()
                )


        # Drop the first column if requested
        if drop_first_col and df.shape[1] > 0:
            df = df.iloc[:, 1:]

        print(f"✅✅✅ Found {len(df)} participants registered to this race. ✅✅✅")
        
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
            cells = [td.get_text(strip=True).replace('\xa0', ' ') for td in tr.find_all("td")]
            if cells:
                rows.append(cells)

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=["שם פרטי", "שם משפחה", "שנת לידה", "מגדר", "מקצה", "קבוצה"])

        # Normalize gender column
        for gender_col in ['מגדר', 'מין']:
            if gender_col in df.columns:
                df[gender_col] = (
                    df[gender_col].replace({'זכר': 'male', 'נקבה': 'female'}).str.strip()
                )

        print(f"✅✅✅ Found {len(df)} participants registered to this race. ✅✅✅")

        return df

    def scrape_participants_table(self):
        url_lower = self.url.lower()
        if "realtiming.co.il" in url_lower:
            df = self.scrape_realtiming_participants_table()
        elif "3plus.co.il" in url_lower or "shvoong" in url_lower:
            df = self.scrape_3plus_participants_table()
        elif "modiin" in url_lower:
            df = self.scrape_modiin_participants_table()
        else:
            raise ValueError("Unknown event URL")

        self.participants_table_df = df
        return df

    def get_filtered_names_3plus_realtiming(self, min_year=None, max_year=None, gender=None, race_keyword=None):
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
        df['שנת לידה'] = df['שנת לידה'].apply(self.normalize_year)

        # Apply filters
        if min_year is not None:
            df = df[df['שנת לידה'] >= min_year]
        if max_year is not None:
            df = df[df['שנת לידה'] <= max_year]
        if gender is not None:
            df = df[df['מגדר'] == gender]
        if race_keyword is not None:
            # First try direct contains
            mask = df['מקצה'].astype(str).str.contains(race_keyword, case=False, na=False)
            
            # Also check normalized distance if no matches found
            if not mask.any() and race_keyword in ["5K", "10K", "15K", "21K", "42K"]:
                normalized_race = race_keyword
                mask = df['מקצה'].apply(lambda x: str(self.normalize_distance(str(x)))) == normalized_race
            
            df = df[mask]

        # Build list of tuples
        self.names_list = list(df[['שם פרטי', 'שם משפחה']].itertuples(index=False, name=None))
        return self.names_list

    def get_filtered_names_shvoong(self, min_year=1976, max_year=1985, gender='male', race_keyword=None):
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
                mask = df['מקצה'].apply(lambda x: str(self.normalize_distance(str(x)))) == race_keyword
            else:
                # Try direct contains for non-standard race categories
                mask = df['מקצה'].astype(str).str.contains(race_keyword, case=False, na=False)
            
            df = df[mask]

        # Build list of tuples
        if len(df) > 0:
            self.names_list = list(df[['שם פרטי', 'שם משפחה']].itertuples(index=False, name=None))
        else:
            self.names_list = []
            
        return self.names_list

    def get_filtered_names(self, min_year=1976, max_year=1985, gender='male', race_keyword=None):
        url_lower = self.url.lower()

        # Remember the filter years so we can reflect the age range in the output filename later
        self.min_year_param = min_year
        self.max_year_param = max_year

        if "realtiming.co.il" in url_lower:
            return self.get_filtered_names_3plus_realtiming(min_year=min_year, max_year=max_year, gender=gender, race_keyword=race_keyword)
        elif "3plus.co.il" in url_lower or "modiin" in url_lower:
            return self.get_filtered_names_3plus_realtiming(min_year=min_year, max_year=max_year, gender=gender, race_keyword=race_keyword)
        elif "shvoong" in url_lower:
            if "21" in race_keyword:
                race_keyword = 'חצי מרתון'
            return self.get_filtered_names_shvoong(min_year=min_year, max_year=max_year, gender=gender, race_keyword=race_keyword)

    @staticmethod
    def normalize_distance(value):
        if pd.isna(value) or str(value).strip() == "":
            return np.nan
        s = str(value).strip()
        # if s in ["10 ק\"מ", "10ק\"מ", "9800", "10000", "10 קמ", "10 km - competitive"]:
        if s in ["10 ק\"מ", "10ק\"מ", "9800", "10000", "10 קמ"]:
            return "10K"
        # if s in ["21097", "21000", "21K", "21k"]:
        if s in ["21097", "21 ק\"מ", "21000", "21K", "21k", "חצי מרתון", "חצי מרתון תחרותי", "חצי-מרתון", "חצי_מרתון"]:
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

    def fetch_best_result(self, first_name, last_name, category, timeout_seconds=10):
        query = quote(f"{first_name} {last_name}")
        url = f"https://raceresults.shvoong.co.il/race-result/?q={query}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/141.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=timeout_seconds)
            response.raise_for_status()
        except Timeout:
            print(f"⏰ Timeout for {first_name} {last_name} after {timeout_seconds}s")
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

        # Normalize category and pick best time string
        df["normalized_distance"] = df["מקצה"].apply(self.normalize_distance)
        df["תוצאה מיטבית"] = df.apply(self.choose_best_time_string, axis=1)

        # Convert to timedelta for sorting
        df["race_time"] = pd.to_timedelta(df["תוצאה מיטבית"], errors="coerce")

        # Filter by category
        df_cat = df[df["normalized_distance"] == category]
        if df_cat.empty:
            print(f"⚠️ No results for {first_name} {last_name} in category {category}")
            return None

        # Find best result
        best_idx = df_cat["race_time"].idxmin()
        best_row = df_cat.loc[best_idx].copy()
        best_row["שם פרטי"] = first_name
        best_row["שם משפחה"] = last_name
        best_row["הערה"] = "Best Result"

        return best_row

    def best_results_for_category(self, category):
        best_results = []

        for first_name, last_name in self.names_list:
            best_row = self.fetch_best_result(first_name, last_name, category)
            if best_row is not None:
                best_results.append(best_row)

        if not best_results:
            print("❌ No best results found for any person")
            return

        df_best = pd.DataFrame(best_results)
        df_best.reset_index(drop=True, inplace=True)

        # ✅ תוצאה מיטבית sorting step
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
                oldest_age = current_year - min_year    # lower birth year -> older
                age_suffix = f"_{youngest_age}-{oldest_age}"

            output_file = f"excel/{timestamp}_{self.race_name}_best_results_{category}{age_suffix}.xlsx"
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                df_best.to_excel(writer, index=False)
            print(f"✅ Saved best results for category '{category}' to {output_file}")
            
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

    names_filtered = test.get_filtered_names(min_year=1970, max_year=2005, gender='male', race_keyword='21')
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
