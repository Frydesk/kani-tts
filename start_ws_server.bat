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

REM Start the WebSocket server
python start_websocket_server.py

endlocal
