@echo off
setlocal

:: Set PYTHONPATH to the project root for development mode
set PYTHONPATH=%~dp0

:: Run the CLI entry point
python "%~dp0foton_system\interfaces\cli\main.py" %*

pause
