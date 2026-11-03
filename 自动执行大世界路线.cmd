@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONUNBUFFERED=1
"%~dp0.venv\Scripts\python.exe" "%~dp0world_solution.py" play
pause
