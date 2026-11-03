@echo off
setlocal
cd /d "%~dp0"
title SheepSolver World v2
set PYTHONUTF8=1
set PYTHONUNBUFFERED=1
set "PYTHONPATH=%~dp0;%~dp0world_support"
if not defined SHEEP_NODE set "SHEEP_NODE=node"
if not exist "%~dp0.venv\Scripts\mitmdump.exe" (
  echo Run setup-world.ps1 first. Python 3.12 and Node.js are required.
  pause
  exit /b 1
)
echo SheepSolver World v2 - proxy 127.0.0.1:6666
echo Close the previous capture window before starting this one.
"%~dp0.venv\Scripts\mitmdump.exe" --listen-host 127.0.0.1 --listen-port 6666 --set flow_detail=0 --set "confdir=%~dp0runtime\mitmproxy" --allow-hosts "(^|\.)(easygame2021\.com|mitm\.it)(:[0-9]+)?$" -s "%~dp0world_capture.py"
pause
