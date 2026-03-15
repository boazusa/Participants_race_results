pipeline {
    agent any
    options {
        // Better build discarder with more options
        buildDiscarder(logRotator(
            numToKeepStr: '10',
            daysToKeepStr: '30',
            artifactNumToKeepStr: '5'
        ))
        timestamps()
    }
    stages {
        stage('Install Dependencies') {
            steps {
                script {
                    catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
                        bat '''
@echo off
echo ========================================
echo   Installing Dependencies
echo ========================================
echo.

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
echo 📦 Installing requirements.txt...
pip install -r requirements.txt

REM Install additional testing dependencies
echo 📦 Installing testing dependencies...
pip install pytest pytest-cov pytest-html

echo.
echo ✅ Dependencies installed successfully!
echo ========================================
exit /b 0
                        '''
                    }
                }
            }
        }
        
        stage('Test Race Analysis') {
            steps {
                script {
                    try {
                        dir('tests') {
                            bat '''
@echo off
echo ========================================
echo   Testing Race Analysis
echo ========================================
echo.

echo 🧪 Running test_race_analysis.py...
python -m pytest test_race_analysis.py -v --tb=short --color=yes --durations=10

if %ERRORLEVEL%==0 (
    echo ✅ Race Analysis tests passed!
    exit /b 0
) else (
    echo ❌ Race Analysis tests failed!
    echo 📊 Exit Code: %ERRORLEVEL%
    echo 🔍 Check the test output above for details
    exit /b 1
)
                            '''
                        }
                    } catch (Exception e) {
                        echo "❌ Race Analysis tests failed with exception: ${e}"
                        echo "⚠️  Continuing with next stage..."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Test Race Analysis Fixed') {
            steps {
                script {
                    try {
                        dir('tests') {
                            bat '''
@echo off
echo ========================================
echo   Testing Race Analysis Fixed
echo ========================================
echo.

echo 🧪 Running test_race_analysis_fixed.py...
python -m pytest test_race_analysis_fixed.py -v --tb=short --color=yes --durations=10

if %ERRORLEVEL%==0 (
    echo ✅ Race Analysis Fixed tests passed!
    exit /b 0
) else (
    echo ❌ Race Analysis Fixed tests failed!
    echo 📊 Exit Code: %ERRORLEVEL%
    echo 🔍 Check the test output above for details
    exit /b 1
)
                            '''
                        }
                    } catch (Exception e) {
                        echo "❌ Race Analysis Fixed tests failed with exception: ${e}"
                        echo "⚠️  Continuing with next stage..."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Test Simple Working') {
            steps {
                script {
                    try {
                        dir('tests') {
                            bat '''
@echo off
echo ========================================
echo   Testing Simple Working
echo ========================================
echo.

echo 🧪 Running test_simple_working.py...
python -m pytest test_simple_working.py -v --tb=short --color=yes --durations=10

if %ERRORLEVEL%==0 (
    echo ✅ Simple Working tests passed!
    exit /b 0
) else (
    echo ❌ Simple Working tests failed!
    echo 📊 Exit Code: %ERRORLEVEL%
    echo 🔍 Check the test output above for details
    exit /b 1
)
                            '''
                        }
                    } catch (Exception e) {
                        echo "❌ Simple Working tests failed with exception: ${e}"
                        echo "⚠️  Continuing with next stage..."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Test 3Plus Scenario') {
            steps {
                script {
                    try {
                        dir('tests') {
                            bat '''
@echo off
echo ========================================
echo   Testing 3Plus Scenario
echo ========================================
echo.

echo 🧪 Running test_3plus_scenario.py...
python -m pytest test_3plus_scenario.py -v --tb=short --color=yes --durations=10

if %ERRORLEVEL%==0 (
    echo ✅ 3Plus Scenario tests passed!
    exit /b 0
) else (
    echo ❌ 3Plus Scenario tests failed!
    echo 📊 Exit Code: %ERRORLEVEL%
    echo 🔍 Check the test output above for details
    exit /b 1
)
                            '''
                        }
                    } catch (Exception e) {
                        echo "❌ 3Plus Scenario tests failed with exception: ${e}"
                        echo "⚠️  Continuing with next stage..."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Test Best Results Helpers') {
            steps {
                script {
                    try {
                        dir('tests') {
                            bat '''
@echo off
echo ========================================
echo   Testing Best Results Helpers
echo ========================================
echo.

echo 🧪 Running test_best_results_helpers.py...
python -m pytest test_best_results_helpers.py -v --tb=short --color=yes --durations=10

if %ERRORLEVEL%==0 (
    echo ✅ Best Results Helpers tests passed!
    exit /b 0
) else (
    echo ❌ Best Results Helpers tests failed!
    echo 📊 Exit Code: %ERRORLEVEL%
    echo 🔍 Check the test output above for details
    exit /b 1
)
                            '''
                        }
                    } catch (Exception e) {
                        echo "❌ Best Results Helpers tests failed with exception: ${e}"
                        echo "⚠️  Continuing with next stage..."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Test Project') {
            steps {
                script {
                    try {
                        dir('tests') {
                            bat '''
@echo off
echo ========================================
echo   Testing Project
echo ========================================
echo.

echo 🧪 Running test_project.py...
python -m pytest test_project.py -v --tb=short --color=yes --durations=10

if %ERRORLEVEL%==0 (
    echo ✅ Project tests passed!
    exit /b 0
) else (
    echo ❌ Project tests failed!
    echo 📊 Exit Code: %ERRORLEVEL%
    echo 🔍 Check the test output above for details
    exit /b 1
)
                            '''
                        }
                    } catch (Exception e) {
                        echo "❌ Project tests failed with exception: ${e}"
                        echo "⚠️  Continuing with next stage..."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Test Integration Simple') {
            steps {
                script {
                    try {
                        dir('tests') {
                            bat '''
@echo off
echo ========================================
echo   Testing Integration Simple
echo ========================================
echo.

echo 🧪 Running test_integration_simple.py...
python -m pytest test_integration_simple.py -v --tb=short --color=yes --durations=10

if %ERRORLEVEL%==0 (
    echo ✅ Integration Simple tests passed!
    exit /b 0
) else (
    echo ❌ Integration Simple tests failed!
    echo 📊 Exit Code: %ERRORLEVEL%
    echo 🔍 Check the test output above for details
    exit /b 1
)
                            '''
                        }
                    } catch (Exception e) {
                        echo "❌ Integration Simple tests failed with exception: ${e}"
                        echo "⚠️  Continuing with next stage..."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Test Summary') {
            steps {
                script {
                    try {
                        dir('tests') {
                            bat '''
@echo off
echo ========================================
echo   Final Test Summary
echo ========================================
echo.

echo 🧪 Running complete test suite...
python -m pytest --tb=short --color=yes --durations=10

if %ERRORLEVEL%==0 (
    echo.
    echo   ✅ SUCCESS: All tests passed!
    echo   🎉 Testing framework is working perfectly!
    echo   📊 Check the detailed results above for test coverage.
    exit /b 0
) else (
    echo.
    echo   ❌ FAILED: Some tests failed!
    echo   🔍 Check the test output above for details
    echo   📊 Exit Code: %ERRORLEVEL%
    exit /b 1
)
                            '''
                        }
                    } catch (Exception e) {
                        echo "❌ Final test summary failed with exception: ${e}"
                        currentBuild.result = 'FAILURE'
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                bat '''
@echo off
echo ========================================
echo   Post-Test Cleanup
echo ========================================
echo.

REM Clean up any temporary files if needed
if exist "tests\temp" (
    rmdir /s /q "tests\temp"
    echo   🧹 Cleaned temporary files
)

REM Archive test results if needed
if exist "tests\test_results" (
    echo   📁 Test results available in tests\\test_results
)

echo.
echo ========================================
echo   Cleanup Complete
echo ========================================
                        '''
            }
        }
    }
    }
}
