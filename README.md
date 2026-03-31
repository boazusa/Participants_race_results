# Running Records Analysis

Professional race results analysis platform with web interface for scraping, filtering, and analyzing race participant data.

## 🏃 Quick Start

### Run Main Application
```bash
python run_main_app.py
```
Access at: http://127.0.0.1:5000

### Run Single Person Analysis
```bash
python run_single_person_app.py
```
Access at: http://127.0.0.1:5001

## 📁 Project Structure

```
running_records/
├── src/                         # Source code
│   ├── core/                    # Business logic
│   │   ├── race_analyzer.py     # Main race results analyzer
│   │   ├── excel_processor.py   # Excel file processor
│   │   └── single_person_analyzer.py  # Single person analysis
│   ├── web/                     # Flask applications
│   │   ├── main_app.py          # Main web app
│   │   ├── single_person_app.py # Single person app
│   │   ├── templates/           # HTML templates
│   │   └── static/              # CSS, images
│   └── utils/                   # Utilities
├── tests/                       # Test suite
├── docs/                        # Documentation
├── config/                      # Configuration files
├── scripts/                     # Automation scripts
└── data/                        # Data storage
```

## 🔧 Installation

```bash
pip install -r config/requirements.txt
```

## 🧪 Testing

```bash
# Run all tests
scripts/run_tests.bat

# Run specific test file
python -m pytest tests/test_race_analysis.py -v
```

## 📊 Features

- **Web Scraping**: Automatic participant data extraction from race websites
- **Filtering**: Age, gender, and race distance filters
- **Best Results**: Find each participant's best historical race times
- **Excel Export**: Download results as Excel files
- **History**: Save and rerun previous analyses

## 📝 License

Built by Boaz Bilgory
