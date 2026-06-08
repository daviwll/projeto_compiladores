@echo off
REM Minipar Compiler Web Interface Launcher
REM Windows batch file to start the web interface

echo ============================================================
echo   Minipar Compiler - Web Interface Launcher
echo ============================================================
echo.

REM Navigate to project root
cd /d "%~dp0\.."

REM Check if uv is available
where uv >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv not found!
    echo Please install uv from: https://docs.astral.sh/uv/
    echo Or run: pip install uv
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
py --version 2>nul || python --version
echo.

REM Check if venv exists, if not run uv sync
if not exist ".venv\Scripts\python.exe" (
    echo [2/4] Virtual environment not found. Running uv sync...
    uv sync
    echo.
) else (
    echo [2/4] Virtual environment found
    echo.
)

REM Check if Gradio is installed, if not run uv sync
.venv\Scripts\python.exe -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo [3/4] Gradio not found. Installing dependencies...
    uv sync
    echo.
) else (
    echo [3/4] Gradio already installed
    echo.
)

REM Navigate to interface directory
cd interface

echo [4/4] Starting web interface...
echo.
echo ============================================================
echo   The interface will open in your browser
echo   URL: http://localhost:7860
echo.
echo   Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the interface using venv Python
..\\.venv\Scripts\python.exe app.py

pause
