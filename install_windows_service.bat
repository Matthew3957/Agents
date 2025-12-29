@echo off
REM Windows Service Installation Script for Ollama Multi-Agent Assistant
REM Run this as Administrator

echo ========================================
echo Ollama Multi-Agent Assistant - Windows Service Setup
echo ========================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Install NSSM if not present
where nssm >nul 2>&1
if %errorLevel% neq 0 (
    echo NSSM not found. Please install NSSM from https://nssm.cc/
    echo.
    echo Quick install with chocolatey:
    echo   choco install nssm
    echo.
    pause
    exit /b 1
)

REM Get current directory
set APP_DIR=%~dp0
set APP_PATH=%APP_DIR%ollama_multi_agent_tray.py

REM Find Python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i

echo Installing service...
echo Python: %PYTHON_PATH%
echo App: %APP_PATH%
echo.

REM Remove existing service if present
nssm remove OllamaAssistant confirm >nul 2>&1

REM Install service
nssm install OllamaAssistant "%PYTHON_PATH%" "%APP_PATH%"
nssm set OllamaAssistant AppDirectory "%APP_DIR%"
nssm set OllamaAssistant DisplayName "Ollama Multi-Agent Assistant"
nssm set OllamaAssistant Description "AI assistant with intelligent agent routing"
nssm set OllamaAssistant Start SERVICE_AUTO_START
nssm set OllamaAssistant AppStopMethodSkip 0

echo.
echo Service installed successfully!
echo.
echo To start the service:
echo   nssm start OllamaAssistant
echo.
echo To stop the service:
echo   nssm stop OllamaAssistant
echo.
echo To remove the service:
echo   nssm remove OllamaAssistant confirm
echo.
echo Starting service now...
nssm start OllamaAssistant

echo.
echo Done! The assistant should now be running in the background.
echo Press Ctrl+Shift+A to access the interface.
echo.
pause
