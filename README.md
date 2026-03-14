# Running Records – Best Race Results GUI

Author: Boaz Bilgory

## Overview

This project provides a small Flask web application and core Python logic to:

- Scrape race participant data from supported event provider sites (3plus, RealTiming, Modiin, Shvoong).
- Filter participants by year of birth, gender, and current race category.
- Query historical race results per participant and compute each person’s best result in a chosen category (e.g. 5K, 10K, 21K).
- Present the top results in a simple web GUI and export full results to Excel.

The UI includes:

- A form to configure the event URL, filters, and best-result category.
- A processing indicator with a timer and three pseudo-steps.
- Light / dark theme toggle.

## Project structure

- `flask_app.py`  – Flask web server and routes (`/` for the GUI, `/download` for Excel files).
- `best_results_3plus_or_realtiming_race.py` – Core scraping, filtering and best-result computation logic.
- `templates/index.html` – Web UI template (Bootstrap-based) used by Flask.
- `tests/` – Complete testing framework with 166 passing tests.
- `requirements.txt` – Python dependencies.
- `excel/` – Output folder for generated Excel files (created automatically at runtime).

## Testing

The project includes a comprehensive testing framework with **166 passing tests** located in the `tests/` folder:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=best_results_3plus_or_realtiming_race

# Run specific test file
pytest tests/test_race_analysis.py -v
```

### Test Coverage:
- ✅ Race analysis functionality (63 tests)
- ✅ Data normalization (44 tests) 
- ✅ Web scraping (6 tests)
- ✅ Error handling (9 tests)
- ✅ Helper functions (13 tests)
- ✅ Flask application (6 tests)

For detailed testing documentation, see `tests/README_TESTING.md`.

## Prerequisites

- Python 3.9+ (recommended).
- `pip` for installing packages.

## Installation

From the project root (`running_records_windsurf` directory):

```bash
pip install -r requirements.txt
```

If you use a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Flask app

From the project root:

```bash
python flask_app.py
```

By default the app runs in debug mode on `http://127.0.0.1:5000/`.

1. Open the URL in your browser.
2. Fill in:
   - **Event URL** – URL of the race participants page (3plus / RealTiming / Modiin / Shvoong).
   - **Race Name** – Used in the output Excel filename (defaults to `NA` if left empty).
   - **Min / Max Year** – Year-of-birth filters.
   - **Gender** – `זכר` (male) or `נקבה` (female).
   - **Current Race Category** – 5K, 10K, 21K for the current event.
   - **Best Result Category** – Category in which to search each participant’s best-ever result.
3. Click **Run**.

While processing, you will see:

- A **processing spinner + timer**.
- Step messages:
  - Step 1/3: Scraping participants…
  - Step 2/3: Filtering participants…
  - Step 3/3: Computing best results…

When done, the page shows:

- Top 10 best results in a table.
- A button to **download the full Excel file** with all computed results.

## Output files

- Participants and best results are written to the `excel/` directory.
- Filenames include:
  - Timestamp
  - Race name
  - Category (e.g. `10K`)

Example:

```text
excel/2024_01_01_12_30_00_באר יעקב_best_results_10K.xlsx
```

## Running the unit tests

From the project root:

For basic helper tests (unittest):
```bash
python -m unittest test_best_results_helpers.py
```

For comprehensive tests (pytest):
```bash
pytest test_project.py
```

The tests cover:

- `normalize_distance` and `normalize_year` – mapping and normalizing data.
- `choose_best_time_string` – picking valid time strings.
- Scraping functions with mocked HTTP responses.
- Filtering logic (`get_filtered_names_*`).
- Flask app routes.

## Notes and limitations

- **External dependencies**: Scraping relies on the HTML structure of external sites; if they change their layout, scraping logic may need updating.
- **Performance**: The app runs all work inside a single HTTP request. For very large events or many historical lookups, consider moving the heavy work to a background job system.
- **Network access**: Computing best results performs HTTP requests to external race results pages; long or unstable connections will slow down processing.

## Future improvements

- More robust error handling and user-visible error messages (bad URL, no table found, network errors).
- Background job queue for long-running scraping and best-result computation.
- Additional unit tests for filtering logic (`get_filtered_names_*`) – now implemented in `test_project.py`.
