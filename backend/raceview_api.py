#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
Project: Running Records Analysis
Module: RaceView API Client
Description:
    Wrapper around the RaceView API for:
    - Authentication
    - Runner search
    - Results retrieval
    - Data processing

Author: Boaz Bilgory
Email: boazusa@hotmail.com
Created: 01/06/2026

Special Thanks:
    Ilan Zisser and the RaceView team for providing API access
    and supporting the running community.

API Provider:
    RaceView

Version: 1.0.0
Python: 3.8+

===============================================================================
"""

from datetime import datetime
import pandas as pd
import json
import requests
from urllib.parse import quote
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RaceViewEngine:

    def __init__(self, api):
        self.api = api

    def get_runner_results(self, full_name):
        data = self.api.search_runner(full_name)
        return data.get("data", {}).get("results", [])

    def filter_by_years(self, df, years_back):
        current_year = datetime.now().year
        min_year = current_year - years_back

        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        return df[
            (df["date"].dt.year >= min_year) &
            (df["date"].dt.year <= current_year)
        ]

    def filter_by_distance(self, df, category):
        distance_map = {
            "5K": 5000,
            "10K": 10000,
            "15K": 15000,
            "21K": 21000,
            "42K": 42195
        }

        target = distance_map.get(category)
        if not target:
            return pd.DataFrame()

        tolerance = 200

        return df[
            (df["distance"] >= target - tolerance) &
            (df["distance"] <= target + tolerance)
        ]

    def pick_best_result(self, df):
        df["best_time"] = (
            pd.to_numeric(df["personal_time"], errors="coerce")
            .fillna(pd.to_numeric(df["result"], errors="coerce"))
        )

        df = df[df["best_time"].notna()]
        if df.empty:
            return None

        return df.loc[df["best_time"].idxmin()]


class RaceViewAPI:
    """
    RaceView API client.

    API access provided by RaceView.
    Special thanks to Ilan Zisser from RaceView for assistance and support.
    """

    BASE_URL = "https://il.raceview.net"

    def __init__(self, email, password, api_key):
        self.email = email
        self.password = password
        self.api_key = api_key
        self.token = None

    def login(self):

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "email": self.email,
            "cred": self.password
        }

        urls = [
            f"{self.BASE_URL}/api/v2.0/user/login/",
            f"{self.BASE_URL}/api/v2.0/user/login",
            f"{self.BASE_URL}/api/v2/user/login/",
            f"{self.BASE_URL}/api/v2/user/login",
        ]

        for url in urls:

            print(f"\nTrying: {url}")

            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30,
                    verify=False
                )

                print("STATUS:", response.status_code)
                print(response.text[:500])

                if response.ok:
                    data = response.json()

                    self.token = (
                        data.get("token")
                        or data.get("Token")
                        or data.get("access_token")
                    )

                    print("TOKEN:", self.token)

                    return self.token

            except Exception as e:
                print(e)

        raise Exception("Could not login")

    def search_runner(self, full_name):
        try:

            if not self.token:
                self.login()

            encoded_name = quote(full_name)

            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "search_type": 1
            }

            url = (
                f"{self.BASE_URL}/api/v2.0/results/search/"
                f"{encoded_name}?token={self.token}"
            )

            print("\nSEARCH URL:")
            print(url)

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30,
                verify=False
            )

            # print("\nSEARCH STATUS:")
            # print(response.status_code)

            # print("\nSEARCH RESPONSE:")
            # print(response.text[:1000])

            response.raise_for_status()

            data = response.json()

            # print("\nJSON RESPONSE:")
            # print(json.dumps(data, indent=4, ensure_ascii=False))

            return data
        except RequestException as e:
            print(f"RaceView API failed for {full_name}: {e}")
            return None


if __name__ == "__main__":
    api = RaceViewAPI(
        email="boazb@gmail.com",
        password="PASSWORD",
        api_key="API_KEY"
    )

    results = api.search_runner("בועז בילגורי")

    with open("runner_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("JSON saved to runner_results.json")

    print("\nFINAL RESULT:")
    # print(json.dumps(results, indent=4, ensure_ascii=False))
