@echo off
setlocal

REM Change to script directory
cd /d %~dp0

REM Check for uv; if not found, install it
where uv >nul 2>&1
if errorlevel 1 (
  echo uv not found. Installing uv...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex"
  REM Attempt to refresh PATH for this session (common install path)
  set "PATH=%USERPROFILE%\.cargo\bin;%USERPROFILE%\.local\bin;%PATH%"
  where uv >nul 2>&1
  if errorlevel 1 (
    echo Failed to install uv. Please open a new shell or install uv manually from https://astral.sh/uv
    goto :eof
  )
)

REM Ensure .venv exists using uv
uv venv .venv
if errorlevel 1 (
  echo Failed to create virtual environment with uv.
  goto :eof
)

REM Activate the environment
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
) else (
  echo Failed to activate .venv environment.
  goto :eof
)

REM Install project dependencies
uv pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed.
  goto :eof
)

echo.
echo ==============================================
echo ✅ Environment ready using uv in .venv
echo To start the WebSocket server run: start_ws_server.bat
echo To run the interactive tester run: test_ws_cli.bat
echo ==============================================
echo.

endlocal
pause