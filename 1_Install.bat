@echo off
title Traffic AI Setup
echo ==========================================
echo    Installing Traffic AI Environment...
echo ==========================================
cd /d "%~dp0"

echo [1/2] Creating virtual environment...
python -m venv .venv

echo [2/2] Installing required packages...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ==========================================
echo    Installation Complete! 
echo    You can now double-click "2_Start_AI.vbs"
echo ==========================================
pause