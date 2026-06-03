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
Last Modified: 04/03/2025
Version: 1.0.1
Python Version: 3.8+
Dependencies:
    - Flask >= 2.0.0
    - pandas >= 1.3.0
    - openpyxl >= 3.0.0
    - gunicorn >= 20.1.0 (for production deployment)
Performance: Designed for small to medium race participant datasets.
             Heavy use may require background job processing.
License: [boazusa@hotmail.com]
===============================================================================
"""

from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from datetime import datetime
import json
import uuid
# from backend.race_analyzer_new import (       # New method via raceview
from backend.race_analyzer_new import (
    best_race_results_per_participant,
)  # <-- your class file

app = Flask(__name__)

HISTORY_FILE = "run_history.json"

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

def to_seconds(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    # case 01:05:54
    if ":" in value:
        parts = value.split(":")
        parts = [int(p) for p in parts]
        if len(parts) == 3:
            h, m, s = parts
            return h * 3600 + m * 60 + s
        if len(parts) == 2:
            m, s = parts
            return m * 60 + s

    # case 2116.66
    try:
        return float(value)
    except:
        return None

def save_history(entry):

    history = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except:
                history = []

    entry["id"] = str(uuid.uuid4())  # ← ID קבוע

    history.insert(0, entry)

    MAX_HISTORY = 50
    history = history[:MAX_HISTORY]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            history = json.load(f)
        except:
            return []

    # 🔥 FIX: ensure every entry has an ID
    changed = False
    for entry in history:
        if "id" not in entry:
            entry["id"] = str(uuid.uuid4())
            changed = True

    # אם הוספנו IDים → נשמור חזרה לקובץ
    if changed:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

    return history


def clean_timedelta(td):
    if pd.isna(td):
        return ""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


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

        # Get years_back from URL parameter or form, default to 5
        years_back = int(request.args.get("years_back", request.form.get("years_back", 5)))

        # ======= Run your class =======
        # excel_path = f"excel/{datetime.now().strftime('%Y%m%d_%H%M%S')}_participants.xlsx"
        runner = best_race_results_per_participant(
            url=event_url,
            race_name=race_name,
            excel_path=True,
            years_back=years_back,  # Filter to past N years only
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
                f
                for f in os.listdir("excel")
                if f.endswith(".xlsx") and race_name in f and not f.startswith("~$")
            ],
            reverse=True,
        )

        if not excel_files:
            return render_template(
                "index.html",
                done=False,
                error_message="No runners found for the selected filters.",
                history=load_history(),
            )

        output_file = "excel/" + excel_files[0]

        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event_url": event_url,
            "race_name": race_name,
            "min_age": min_age,
            "max_age": max_age,
            "age_range": f"{min_age}-{max_age}",
            "gender": gender,
            "race_keyword": race_keyword,
            "category": category,
            "years_back": years_back,
            "file": output_file,
        }

        save_history(history_entry)

        if not os.path.exists(output_file):
            return render_template(
                "index.html",
                done=False,
                error_message="Excel file was not generated.",
                history=load_history(),
            )

        # Load result to show top 10
        df = pd.read_excel(output_file)
        # columns_to_show = [
        #     "שם מרוץ",
        #     "שם פרטי",
        #     "שם משפחה",
        #     "תאריך אירוע",
        #     "תוצאה מיטבית",
        #     "קטגוריה",
        # ]

        columns_to_show = {
            "שם פרטי": "first_name",
            "שם משפחה": "last_name",
            "שם מרוץ": "event_name",
            "תאריך": "date",
            "קטגוריה": "category",  # TODO: remove?
            "מקצה": "race_name",
            # "מרחק": "distance",
            "תוצאה": "result",
            # "זמן אישי": "personal_time",
            "קצב לק״מ": "pace_k"
        }

        # ===== RESULTS STATS =====

        total_runners = len(df)
        df = df.sort_values("result", ascending=True)
        df["race_time"] = pd.to_timedelta(df["result"], errors="coerce")

        fastest_time = df["result"].min()
        avg_time = df["result"].mean()

        print("* Fastest time:", fastest_time)
        print("* Average time:", avg_time)

        print("* Fastest time:", format_seconds(fastest_time))
        print("* Average time:", format_seconds(avg_time))

        # Optional – time of place 10
        top3_cutoff = "N/A"
        if len(df) >= 3:
            cutoff = df["result"].iloc[2]
            if pd.notna(cutoff):
                top3_cutoff = format_seconds(cutoff)
        
        df["result"] = df["result"].apply(format_seconds)

        # fastest_time = df["race_time"].min()
        # avg_time = df["race_time"].mean()
        
        # print("Fastest time:", fastest_time)
        # print("Average time:", avg_time)

        # print("Fastest time:", format_seconds(fastest_time))
        # print("Average time:", format_seconds(avg_time))

        # # Convert to clean strings
        # fastest_time = clean_timedelta(fastest_time)
        # avg_time = clean_timedelta(avg_time)

        fastest_time = format_seconds(fastest_time)
        avg_time = format_seconds(avg_time)

        print("Fastest time:", fastest_time)
        print("Average time:", avg_time)

        df_best = df[list(columns_to_show.values())]
        df_best.columns = list(columns_to_show.keys())

        print(df_best)

        df_best.rename(columns={
            "event_name": "שם מרוץ",
            "date": "תאריך אירוע",
            "category": "קטגוריה",
            "race_name": "מקצה",
            "distance": "מרחק",
            "תוצאה מיטבית": "תוצאה מיטבית",
            "personal_time": "זמן אישי",
            "pace_k": "קצב לק״מ",
            "first_name": "שם פרטי",
            "last_name": "שם משפחה"
        }, inplace=True)
        
        top10 = df_best.head(10).to_html(classes="table table-striped", index=False)

        history = load_history()

        return render_template(
            "index.html",
            table_html=top10,
            download_link=output_file,
            done=True,
            race_name=race_name,
            history=history,
            fastest_time=fastest_time,
            avg_time=avg_time,
            total_runners=total_runners,
            top3_cutoff=top3_cutoff,
        )

    history = load_history()

    # Handle edit parameter - populate form with history data
    edit_data = {}
    edit_id = request.args.get('edit')
    if edit_id and history:
        for run in history:
            if run.get('id') == edit_id:
                edit_data = {
                    'event_url': run.get('event_url', ''),
                    'race_name': run.get('race_name', ''),
                    'min_age': run.get('min_age', ''),
                    'max_age': run.get('max_age', ''),
                    'gender': run.get('gender', ''),
                    'race_keyword': run.get('race_keyword', ''),
                    'category': run.get('category', ''),
                    'years_back': run.get('years_back', '')
                }
                break
    else:
        # Ensure edit_data is always defined for template
        edit_data = {}

    return render_template("index.html", done=False, history=history, edit_data=edit_data)


@app.route("/download")
def download():
    path = request.args.get("path")
    return send_file(path, as_attachment=True)


@app.route("/delete_history/<row_id>", methods=["DELETE"])
def delete_history(row_id):

    history = load_history()

    print("DELETE REQUEST:", row_id)
    print("IDs in file:", [h.get("id") for h in history])

    history = [h for h in history if str(h.get("id")) != str(row_id)]

    print("After filter:", [h.get("id") for h in history])

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    return {"success": True}


"""
 & C:/tools/Python/python.exe c:/Users/USER/Documents/Python/running_records/running_records_windsurf/flask_app.py
 python c:/Users/USER/Documents/Python/running_records/running_records_windsurf/flask_app.py 
"""

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, port=5000)
