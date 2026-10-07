@echo off
setlocal
cd /d "%~dp0" || exit /b 1
if not exist ".venv\Scripts\python.exe" (
    echo The project environment is missing. Follow the setup in README.md first.
    if "%~1"=="" pause
    exit /b 1
)
".venv\Scripts\python.exe" demo.py --warmup %*
set "demo_exit=%errorlevel%"
if "%~1"=="" pause
exit /b %demo_exit%
