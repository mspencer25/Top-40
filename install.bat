@echo off
REM Top 40 Dashboard Installation Script - Windows
REM Drew Shoe Corporation

echo ========================================
echo   Top 40 Dashboard Setup
echo   Drew Shoe Corporation
echo ========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.11 or higher.
    pause
    exit /b 1
)
echo OK: Python found

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist venv (
    echo WARNING: Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo OK: Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo OK: Dependencies installed

REM Create secrets directory
echo.
echo Setting up configuration...
if not exist .streamlit mkdir .streamlit

if exist .streamlit\secrets.toml (
    echo WARNING: secrets.toml already exists. Skipping...
) else (
    echo Creating secrets template...
    copy secrets.toml.template .streamlit\secrets.toml >nul
    echo OK: secrets.toml created
    echo.
    echo IMPORTANT: Edit .streamlit\secrets.toml with your NetSuite credentials!
)

REM Test imports
echo.
echo Testing module imports...
python -c "import streamlit; import pandas; import plotly; import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Some modules failed to import
    pause
    exit /b 1
)
echo OK: All modules imported successfully

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next Steps:
echo.
echo 1. Configure NetSuite credentials:
echo    notepad .streamlit\secrets.toml
echo.
echo 2. Deploy RESTlet to NetSuite:
echo    See README.md section 'NetSuite Setup'
echo.
echo 3. Test the connection:
echo    python test_dashboard.py
echo.
echo 4. Run the dashboard:
echo    streamlit run app.py
echo.
echo For more information, see:
echo   - QUICKSTART.md - 5-minute guide
echo   - README.md - Full documentation
echo   - DEPLOYMENT.md - Production deployment
echo.
echo Need help? Contact: Megan Spencer
echo.
pause
