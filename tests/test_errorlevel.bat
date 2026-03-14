@echo off
echo Testing ERRORLEVEL behavior...
echo.

REM Simulate success
echo Simulating SUCCESS case...
set ERRORLEVEL=0
if %ERRORLEVEL%==0 (
    echo ✅ SUCCESS: ERRORLEVEL is 0
) else (
    echo ❌ FAILED: ERRORLEVEL is %ERRORLEVEL%
)
echo.

REM Simulate failure  
echo Simulating FAILURE case...
set ERRORLEVEL=1
if %ERRORLEVEL%==0 (
    echo ✅ SUCCESS: ERRORLEVEL is 0
) else (
    echo ❌ FAILED: ERRORLEVEL is %ERRORLEVEL%
)
echo.

REM Show current ERRORLEVEL
echo Current ERRORLEVEL is: %ERRORLEVEL%
pause
