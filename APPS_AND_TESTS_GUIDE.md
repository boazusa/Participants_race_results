# 🚀 Apps and Tests Quick Start Guide

## 📱 **Web Applications**

### **1. Main Flask App** (`flask_app.py`)
**Purpose:** Full-featured web interface for race analysis
```bash
# Run the main Flask application
python flask_app.py

# Access in browser
http://localhost:5000
```

**Features:**
- Race result analysis and filtering
- Excel file generation and download
- History management
- Age/gender/category filtering
- Years back filtering

---

### **2. Single Person Flask App** (`single_person_flask_app.py`)
**Purpose:** Search for individual runner results
```bash
# Run single person search app
python single_person_flask_app.py

# Access in browser
http://localhost:5001
```

**Features:**
- Individual runner search
- Top results display
- Multiple race result sources

---

## 🧪 **Running Tests**

### **Quick Test Commands**

#### **Run All Tests** (Recommended)
```bash
# From project root
pytest tests/

# From tests directory
cd tests && pytest

# With verbose output
pytest tests/ -v

# With coverage
pytest tests/ --cov=best_results_3plus_or_realtiming_race
```

#### **Run Specific Test Files**
```bash
# Core functionality tests (63 tests)
pytest tests/test_race_analysis.py -v

# Basic working tests (10 tests)
pytest tests/test_simple_working.py -v

# Helper function tests (13 tests)
pytest tests/test_best_results_helpers.py -v

# 3Plus scenario tests (11 tests)
pytest tests/test_3plus_scenario.py -v

# Project integration tests (6 tests)
pytest tests/test_project.py -v
```

#### **Run Test Categories**
```bash
# Unit tests only
pytest tests/ -m unit

# Web scraping tests only
pytest tests/ -m web_scraping

# Integration tests only
pytest tests/ -m integration

# Performance tests only
pytest tests/ -m performance
```

---

### **Batch File Runners**

#### **Main Test Runner** (`tests/run_tests.bat`)
```bash
# Double-click or run from command line
tests\run_tests.bat
```
**Runs:** All 192 tests with professional output

#### **Working Tests Only** (`tests/RUN_WORKING_TESTS.bat`)
```bash
# Quick validation of core functionality
tests\RUN_WORKING_TESTS.bat
```
**Runs:** 10 basic tests for fast validation

#### **Professional Test Runner** (`tests/run_tests_professional.bat`)
```bash
# Enhanced output with timing information
tests\run_tests_professional.bat
```
**Runs:** All tests with duration reporting

---

## 📊 **Test Results Summary**

### **Current Test Suite: 192 Tests**
| Test File | Test Count | Purpose |
|-----------|-------------|---------|
| `test_race_analysis.py` | 63 | Core race analysis functionality |
| `test_race_analysis_fixed.py` | 63 | Backup core tests |
| `test_simple_working.py` | 10 | Basic functionality validation |
| `test_3plus_scenario.py` | 11 | 3Plus website scenarios |
| `test_best_results_helpers.py` | 13 | Helper function tests |
| `test_project.py` | 6 | Project integration tests |
| `test_integration_simple.py` | 5 | Simple integration tests |
| `test_sample_data_integration.py` | 9 | Sample data framework |
| `test_edge_cases_integration.py` | 7 | Edge case handling |
| `test_web_scraping_scenarios.py` | 5 | Web scraping scenarios |

**Total: 192 tests passing** ✅

---

## 🔧 **Development Workflow**

### **1. Quick Development Test**
```bash
# Run basic tests during development
pytest tests/test_simple_working.py -v
```

### **2. Feature Testing**
```bash
# Test specific functionality
pytest tests/test_race_analysis.py::TestNormalizeDistance -v
```

### **3. Full Validation**
```bash
# Run complete test suite before commit
pytest tests/ --cov=best_results_3plus_or_realtiming_race
```

### **4. Performance Testing**
```bash
# Test with large datasets
pytest tests/test_sample_data_integration.py::TestSampleDataIntegration::test_large_dataset_performance -v
```

---

## 🌐 **Web App Usage**

### **Main App Workflow:**
1. **Navigate to:** `http://localhost:5000`
2. **Enter race URL** (e.g., `view-source:https://regi.3plus.co.il/events/page/17492`)
3. **Set filters:**
   - Age range (e.g., 40-49)
   - Gender (male/female)
   - Race keyword (e.g., 10)
   - Category (e.g., 10K)
   - Years back (e.g., 5)
4. **Click "Analyze Race Results"**
5. **View results** and download Excel file

### **Single Person App Workflow:**
1. **Navigate to:** `http://localhost:5001`
2. **Enter runner name** (First + Last name)
3. **Click "Search Results"**
4. **View top 10 results** with race details

---

## 📋 **Requirements Installation**

### **Install Dependencies:**
```bash
# Install all required packages
pip install -r requirements.txt

# Install development dependencies
pip install -r tests/requirements-dev.txt
```

### **Key Dependencies:**
- **Flask** - Web applications
- **pandas** - Data processing
- **requests** - HTTP requests
- **beautifulsoup4** - HTML parsing
- **pytest** - Testing framework
- **openpyxl** - Excel file handling

---

## 🎯 **Common Issues & Solutions**

### **Import Issues:**
```bash
# If imports fail, ensure you're in project root
cd /path/to/running_records_windsurf

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### **Port Conflicts:**
```bash
# If port 5000 is busy, Flask will automatically try next port
# Or specify different port:
python -c "from flask_app import app; app.run(port=5001)"
```

### **Test Failures:**
```bash
# Run with verbose output to see details
pytest tests/ -v --tb=short

# Run specific failing test
pytest tests/test_race_analysis.py::TestNormalizeDistance -v -s
```

---

## 🚀 **Production Deployment**

### **Main App:**
```bash
# Using gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 flask_app:app

# Using built-in Flask (development only)
python flask_app.py
```

### **Single Person App:**
```bash
# Using gunicorn
gunicorn -w 2 -b 0.0.0.0:5001 single_person_flask_app:app
```

---

## 📞 **Quick Reference**

| Action | Command |
|--------|---------|
| **Start Main App** | `python flask_app.py` |
| **Start Single App** | `python single_person_flask_app.py` |
| **Run All Tests** | `pytest tests/ -v` |
| **Run Quick Tests** | `tests\run_tests.bat` |
| **Install Dependencies** | `pip install -r requirements.txt` |
| **View Coverage** | `pytest tests/ --cov=. --cov-report=html` |

---

## 🎉 **Success Indicators**

### **Apps Working:**
- ✅ Flask server starts successfully
- ✅ Web interface loads at localhost
- ✅ Forms accept input and process data
- ✅ Excel files generated in `excel/` folder

### **Tests Working:**
- ✅ All 192 tests pass
- ✅ Coverage report generated
- ✅ No import errors
- ✅ Performance benchmarks met

**Your running records analysis system is ready!** 🏃‍♂️✨
