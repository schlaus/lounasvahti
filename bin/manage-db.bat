@echo off
setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set VENV_PYTHON=%PROJECT_ROOT%\venv\Scripts\python.exe
set DB_SCRIPT=%PROJECT_ROOT%\scripts\manage_db.py

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual environment not found. Did you create it?
    exit /b 1
)

REM Ensure Python knows about the project root
set PYTHONPATH=%PROJECT_ROOT%

"%VENV_PYTHON%" "%DB_SCRIPT%" %*

endlocal
