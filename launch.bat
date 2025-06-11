@echo off
title MCP Server Auto-Installer v2.0

echo ========================================================
echo   MCP Server Auto-Installer v2.0 (Python Edition)
echo   Professional MCP Server Management Tool
echo ========================================================
echo.

:: Change to the script directory first to ensure all paths are relative to the batch file
cd /d "%~dp0"
echo [INFO] Working directory: %CD%

:: Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

:: Display Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo [INFO] Python version: %%i

:: Check if main script exists
if not exist "mcp_installer.py" (
    echo [ERROR] Main script 'mcp_installer.py' not found in current directory
    echo Current directory: %CD%
    echo Please ensure you're running this batch file from the correct folder
    echo.
    pause
    exit /b 1
)

:: Check if requirements.txt exists
if not exist "requirements.txt" (
    echo [ERROR] Requirements file 'requirements.txt' not found
    echo Please ensure all files are in the correct directory
    echo.
    pause
    exit /b 1
)

:: Check if required packages are installed
echo [INFO] Checking Python dependencies...
python -c "import customtkinter, requests, psutil, PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing required Python packages...
    echo [INFO] This may take a few minutes...
    pip install -r "requirements.txt"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        echo Please try running manually: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo [INFO] Dependencies installed successfully
)

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir "logs"
echo [INFO] Log files will be saved to: %CD%\logs

:: Launch the application
echo [INFO] Starting MCP Installer...
echo [INFO] If a GUI window doesn't appear, check for error messages below
echo.
python "mcp_installer.py"
set app_exit_code=%errorlevel%

echo.
if %app_exit_code% equ 0 (
    echo [INFO] Application closed normally
) else (
    echo [WARNING] Application exited with code: %app_exit_code%
    echo Check the logs directory for error details
)
echo.
pause