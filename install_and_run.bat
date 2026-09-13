@echo off
setlocal enabledelayedexpansion
title Image to SVG Toolkit Installer

echo =======================================================
echo     Installing Dependencies & Launching Converter App  
echo =======================================================
echo.

:: 1. Check for Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your Windows PATH variable.
    echo Please download and install Python 3.x from https://www.python.org/downloads/
    echo Make sure to check the box that says "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)

:: 2. Upgrade pip to ensure smooth package resolution
echo [1/3] Updating Python package manager (pip)...
python -m pip install --upgrade pip --user >nul 2>&1

:: 3. Install required requirements using local requirements file
echo [2/3] Installing dependencies (Pillow & pillow-heif for HEIF/HEIC)...
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Default installation failed. Attempting standalone fallbacks...
    python -m pip install Pillow pillow-heif
)

:: 4. Run the Python Graphical App application
echo [3/3] Launching Graphical Converter Interface...
echo.
start "" python image_converter_gui.py

exit
