@echo off
echo ========================================
echo   Running Testing Framework
echo ========================================
echo.

REM Run the working tests
echo Starting test execution...
echo.
python -m pytest -v --tb=short --color=yes
echo.
echo ========================================
echo   TEST EXECUTION SUMMARY
echo ========================================
echo.

REM Check test results and display appropriate message
if %ERRORLEVEL%==0 (
    echo   ✅ SUCCESS: All tests passed!
    echo   🎉 Testing framework is working perfectly!
    echo   📊 Check the detailed results above for test coverage.
) else (
    echo   ❌ FAILED: Some tests failed!
    echo   🔍 Check the detailed output above for failure details.
    echo   📝 Review the error messages to identify issues.
)

echo.
echo ========================================
echo   Test Statistics
echo ========================================
echo   Exit Code: %ERRORLEVEL%
echo   Timestamp: %date% %time%
echo   Test Framework: pytest
echo   Configuration: tests/pytest.ini
echo.
echo   Available Commands:
echo   - pytest --cov=best_results_3plus_or_realtiming_race
echo   - pytest -m unit
echo   - pytest -m web_scraping
echo   - pytest tests/test_race_analysis.py -v
echo ========================================
pause
