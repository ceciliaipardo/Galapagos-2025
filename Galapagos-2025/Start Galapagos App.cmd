@echo off
title Galapagos Car Tracking App
echo.
echo ========================================
echo    Galapagos Car Tracking App
echo ========================================
echo.
echo Starting application...
echo.
cd /d "%~dp0"
py main.py
if errorlevel 1 (
    echo.
    echo Error occurred. Trying alternative method...
    python main.py
)
if errorlevel 1 (
    echo.
    echo Error: Could not start the application.
    echo Please check that Python is installed correctly.
    echo.
    pause
)
