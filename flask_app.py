#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Web Application (Flask)
Description: Web interface for fetching, filtering, and displaying best race results.
             Provides a user-friendly GUI for race result analysis and visualization.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 15/11/2025
Last Modified: 24/11/2025
Version: 1.0.0
Python Version: 3.8+
Dependencies:
    - Flask >= 2.0.0
    - pandas >= 1.3.0
    - openpyxl >= 3.0.0
    - gunicorn >= 20.1.0 (for production deployment)
Performance: Designed for small to medium race participant datasets.
             Heavy use may require background job processing.
License: [Your License, e.g., MIT, Apache 2.0]
===============================================================================
"""

from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from datetime import datetime
from best_results_3plus_or_realtiming_race import best_race_results_per_participant   # <-- your class file

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # Ensure output directory exists
        os.makedirs("excel", exist_ok=True)

        # ======= Read form fields =======
        event_url = request.form.get("event_url")
        race_name = request.form.get("race_name") or "NA"
        # min_year = int(request.form.get("min_year"))
        # max_year = int(request.form.get("max_year"))
        min_age = int(request.form.get("min_age", 40))
        max_age = int(request.form.get("max_age", 49))
        gender = request.form.get("gender")
        race_keyword = request.form.get("race_keyword")
        category = request.form.get("category")

        # ======= Run your class =======
        excel_path = f"excel/{datetime.now().strftime('%Y%m%d_%H%M%S')}_participants.xlsx"
        runner = best_race_results_per_participant(
            url=event_url,
            race_name=race_name,
            excel_path=True,
        )

        # scrape participants
        participants_df = runner.scrape_participants_table()

        # Calculate birth year range from age range
        current_year = datetime.now().year
        min_year = current_year - max_age
        max_year = current_year - min_age

        # filter names
        names = runner.get_filtered_names(
            min_year=min_year,
            max_year=max_year,
            gender=gender,
            race_keyword=race_keyword,
        )

        # compute best results
        runner.best_results_for_category(category)

        # Find newly generated file (last Excel file created)
        excel_files = sorted(
            [
                f for f in os.listdir("excel")
                if f.endswith(".xlsx")
                and race_name in f
                and not f.startswith("~$")
            ],
            reverse=True
        )

        if not excel_files:
            raise Exception("No valid Excel files found for this race.")

        output_file = "excel/" + excel_files[0]


        # Load result to show top 10
        df = pd.read_excel(output_file)
        columns_to_show = [
            "שם מרוץ",
            "שם פרטי",
            "שם משפחה",
            "תאריך אירוע",
            "תוצאה מיטבית",
            "קטגוריה",
        ]

        df_best = df[columns_to_show]
        top10 = df_best.head(10).to_html(classes="table table-striped", index=False)

        return render_template(
            "index.html",
            table_html=top10,
            download_link=output_file,
            done=True
        )

    return render_template("index.html", done=False)


@app.route("/download")
def download():
    path = request.args.get("path")
    return send_file(path, as_attachment=True)


"""
 & C:/tools/Python/python.exe c:/Users/USER/Documents/Python/running_records/running_records_windsurf/flask_app.py
 python c:/Users/USER/Documents/Python/running_records/running_records_windsurf/flask_app.py 
"""

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, port=5000)
