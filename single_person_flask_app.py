#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Project: Running Records Analysis
Module: Single Person Results Web App
Description: Web interface for fetching and displaying individual race results.
             Shows both best results and complete race history.
Author: Boaz Bilgory
Email: boazusa@hotmail.com
Organization: self
Created: 26/11/2025
Last Modified: 26/11/2025
Version: 1.0.0
Python Version: 3.8+
Dependencies:
    - Flask >= 2.0.0
    - pandas >= 1.3.0
    - beautifulsoup4 >= 4.10.0
    - numpy >= 1.21.0
License: [boazusa@hotmail.com]
===============================================================================
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from Single_person_results_w_top_results import fetch_and_process_results

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("single_person_index.html")

@app.route("/get_results", methods=["POST"])
def get_results():
    try:
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        
        if not first_name or not last_name:
            return jsonify({"error": "First name and last name are required"}), 400

        # Get results from the existing function
        print(f"Fetching results for {first_name} {last_name}")
        best_results, all_results = fetch_and_process_results(first_name, last_name)
        
        # Debug: Print column names to help diagnose the issue
        print("Best results columns:", best_results.columns.tolist())
        print("All results columns:", all_results.columns.tolist())
        
        # Select and rename columns for display
        def prepare_table(df):
            print("\nPreparing table with columns:", df.columns.tolist())
            try:
                # Create a copy to avoid modifying the original
                df = df.copy()
                
                required_columns = ['תאריך אירוע', 'שם פרטי', 'שם משפחה', 'זמן אישי', 'תוצאה', 'שם מרוץ']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    print(f"Warning: Missing columns in DataFrame: {missing_columns}")
                
                # Combine 'תוצאה' and 'זמן אישי' into a single 'זמן' column
                if 'תוצאה' in df.columns and 'זמן אישי' in df.columns:
                    df['זמן'] = df['תוצאה'].fillna(df['זמן אישי'])
                elif 'תוצאה' in df.columns:
                    df['זמן'] = df['תוצאה']
                elif 'זמן אישי' in df.columns:
                    df['זמן'] = df['זמן אישי']
                else:
                    print("Warning: Neither 'תוצאה' nor 'זמן אישי' columns found")
                    df['זמן'] = ''  # Add empty time column to prevent errors
                
                # Combine first and last name into a single column
                if 'שם פרטי' in df.columns and 'שם משפחה' in df.columns:
                    df['שם'] = (df['שם פרטי'] + ' ' + df['שם משפחה']).str.strip()
                else:
                    print("Warning: Missing name columns")
                    df['שם'] = ''  # Add empty name column to prevent errors
                
                # Initialize columns to show with required columns
                columns_to_show = ['תאריך אירוע', 'שם', 'שם מרוץ']
                
                # Add מקצה column if available (from normalized_distance)
                if 'normalized_distance' in df.columns:
                    df['מקצה'] = df['normalized_distance']
                    columns_to_show.append('מקצה')
                elif 'מקצה' in df.columns:
                    # If normalized_distance doesn't exist but מקצה does, use that
                    pass  # already in columns_to_show
                    
                # Remove the original distance column if it exists
                if 'מרחק' in df.columns:
                    df = df.drop(columns=['מרחק'])
                if 'distance' in df.columns:
                    df = df.drop(columns=['distance'])
                
                # Add time column
                columns_to_show.append('זמן')
                
                # Only include columns that exist in the DataFrame
                existing_columns = [col for col in columns_to_show if col in df.columns]
                print("Final columns to show:", existing_columns)
                
                return df[existing_columns]
                
            except Exception as e:
                print(f"Error in prepare_table: {str(e)}")
                raise
        
        # Prepare both tables
        best_display = prepare_table(best_results)
        all_display = prepare_table(all_results)
        
        # Convert DataFrames to HTML tables with custom styling
        def format_table(df, table_id):
            return df.to_html(
                classes="table table-striped table-bordered table-hover",
                index=False,
                table_id=table_id,
                border=0,
                justify='right',
                na_rep='',
                formatters={
                    'תאריך אירוע': lambda x: f'<div style="width: 100px; min-width: 100px; max-width: 120px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0.5rem;">{x}</div>',
                    'שם': lambda x: f'<div style="min-width: 120px; max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0.5rem;">{x}</div>',
                    'שם מרוץ': lambda x: f'<div style="min-width: 600px; max-width: 800px; white-space: normal; word-break: break-word; padding: 0.5rem;">{x}</div>',
                    'מקצה': lambda x: f'<div style="width: 50px; min-width: 50px; max-width: 50px; text-align: center; padding: 0.25rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{x}</div>',
                    'זמן': lambda x: f'<div style="width: 80px; min-width: 80px; max-width: 100px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0.5rem;">{x}</div>'
                },
                escape=False
            )
        
        # Generate HTML tables with custom styling
        best_table = format_table(best_display, "best-results-table")
        all_table = format_table(all_display, "all-results-table")
        
        # Wrap tables in scrollable containers
        best_table = f'<div style="width: 100%; overflow-x: auto; margin-bottom: 2rem;">{best_table}</div>'
        all_table = f'<div style="width: 100%; overflow-x: auto;">{all_table}</div>'
        
        return jsonify({
            "success": True,
            "best_table": best_table,
            "all_table": all_table,
            "result_count": len(all_display)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }), 500


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    
    # Create the template file if it doesn't exist
    template_path = os.path.join("templates", "single_person_index.html")
    if not os.path.exists(template_path):
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>תוצאות מרוצים</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
        .result-section { margin-bottom: 30px; }
        .loading { display: none; text-align: center; margin: 20px 0; }
        #result-count { font-weight: bold; margin: 10px 0; }
        /* Make the race name column (4th column) wider */
        .table td:nth-child(4),
        .table th:nth-child(4) {
            min-width: 400px !important;
            max-width: 400px !important;
            width: 400px !important;
            white-space: normal !important;
            word-break: break-word;
        }
        
        /* Make other columns more compact */
        .table td:not(:nth-child(4)),
        .table th:not(:nth-child(4)) {
            white-space: nowrap;
            width: auto;
        }
        /* Ensure the table is responsive */
        .table-responsive {
            overflow-x: auto;
        }
        .table td {
            white-space: nowrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">חיפוש תוצאות מרוצים</h1>
        
        <div class="row justify-content-center">
            <div class="col-md-6">
                <form id="search-form" class="mb-4">
                    <div class="mb-3">
                        <label for="first_name" class="form-label">שם פרטי</label>
                        <input type="text" class="form-control" id="first_name" required>
                    </div>
                    <div class="mb-3">
                        <label for="last_name" class="form-label">שם משפחה</label>
                        <input type="text" class="form-control" id="last_name" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">חפש תוצאות</button>
                </form>
                
                <div id="loading" class="loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">טוען...</span>
                    </div>
                    <p>מחפש תוצאות, אנא המתן...</p>
                </div>
                
                <div id="result-count" class="text-center"></div>
                
                <div id="results" style="display: none;">
                    <div class="result-section">
                        <h3>התוצאות הטובות ביותר</h3>
                        <div id="best-results" class="table-responsive"></div>
                    </div>
                    
                    <div class="result-section">
                        <h3>כל התוצאות</h3>
                        <div id="all-results" class="table-responsive"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        $(document).ready(function() {
            $('#search-form').on('submit', function(e) {
                e.preventDefault();
                const firstName = $('#first_name').val().trim();
                const lastName = $('#last_name').val().trim();
                
                if (!firstName || !lastName) {
                    alert('נא למלא את השם הפרטי והמשפחה');
                    return;
                }
                
                // Show loading
                $('#loading').show();
                $('#results').hide();
                $('#result-count').empty();
                
                // Send request
                $.ajax({
                    url: '/get_results',
                    method: 'POST',
                    data: {
                        first_name: firstName,
                        last_name: lastName
                    },
                    success: function(response) {
                        if (response.success) {
                            $('#best-results').html(response.best_table);
                            $('#all-results').html(response.all_table);
                            $('#result-count').text(`נמצאו ${response.result_count} תוצאות`);
                            $('#results').show();
                        } else {
                            alert(response.error || 'אירעה שגיאה בעת שליפת הנתונים');
                        }
                    },
                    error: function() {
                        alert('אירעה שגיאה בעת שליפת הנתונים');
                    },
                    complete: function() {
                        $('#loading').hide();
                    }
                });
            });
        });
    </script>
</body>
</html>
""")
    
    app.run(debug=True, port=5001)

    