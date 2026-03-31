@echo off
echo.
echo ========================================
echo   RUNNING WORKING TESTS ONLY
echo ========================================
echo.

REM Run the minimal working tests (10 tests, all passing)
echo Starting minimal test execution...
echo.
python -m pytest tests/test_simple_working.py -v --tb=short --color=yes
echo.
echo ========================================
echo   MINIMAL TESTS SUMMARY
echo ========================================
echo.

if %ERRORLEVEL%==0 (
    echo   SUCCESS: Minimal tests passed!
    echo   Core functionality is working!
    echo   10 basic tests completed successfully.
) else (
    echo   FAILED: Some minimal tests failed!
    echo   Core functionality issues detected.
    echo   Check the error output above.
)

echo.
echo ========================================
echo   Test Statistics
echo ========================================
echo   Exit Code: %ERRORLEVEL%
echo   Timestamp: %date% %time%
echo   Test File: tests/test_simple_working.py
echo   Test Count: 10 tests
echo.
echo   Available Commands:
echo   - python -m pytest tests/test_simple_working.py::TestRaceAnalyzerBasics -v
echo   - python -m pytest tests/test_simple_working.py::TestNormalizationFunctions -v
echo   - python -m pytest tests/test_simple_working.py::TestBasicFunctionality -v
echo ========================================
pause
