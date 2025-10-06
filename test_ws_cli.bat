@echo off
setlocal

REM Change to script directory
cd /d %~dp0

REM Prefer .venv, then venv
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
  call venv\Scripts\activate.bat
)

REM Run the interactive WebSocket tester
echo Starting Kani TTS WebSocket Test CLI...
python test_ws_cli.py

endlocal
pause