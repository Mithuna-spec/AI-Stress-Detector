@echo off
cd /d "%~dp0"
title AI Stress Detector Server
echo ===================================================
echo Starting AI Stress Detector Backend...
echo ===================================================

if not exist venv\Scripts\python.exe (
    echo PYTHON NOT FOUND IN VENV!
    echo Please run 'setup_environment.bat' first.
    pause
    exit /b
)

echo Running server...
venv\Scripts\python.exe server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ---------------------------------------------------
    echo SERVER CRASHED! (Error Code: %ERRORLEVEL%)
    echo Please take a screenshot of this error and share it.
    echo ---------------------------------------------------
    pause
)
pause
