@echo off
echo Starting Galapagos Car Tracking App...
cd /d "%~dp0"
py main.py
if errorlevel 1 (
    echo.
    echo Error occurred. Trying with python command...
    python main.py
)
if errorlevel 1 (
    echo.
    echo Error occurred. Please check if Python is installed correctly.
    pause
)
