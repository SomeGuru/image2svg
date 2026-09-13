@echo off
setlocal enabledelayedexpansion
title Image to SVG Automated Environment Bootstrapper

echo =======================================================================
echo          IMAGE TO SVG TOOLKIT - AUTOMATED WINDOWS INSTALLER
echo =======================================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [CRITICAL ERROR] Python could not be detected in your Windows PATH workspace system env.
    echo Please install Python and ensure "Add Python to PATH" is ticked on installation.
    pause
    exit /b
)

echo [STATUS 1/3] Refreshing pip packaging installer subsystem...
python -m pip install --upgrade pip --user >nul 2>&1

echo [STATUS 2/3] Installing workspace dependencies...
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [WARNING] Dependency mapping failed. Attempting force resolution...
    python -m pip install Pillow pillow-heif requests
)

echo [STATUS 3/3] Execution array cleared. Opening Graphical Vectorization App UI...
echo.
start "" python image_converter_gui.py
exit
