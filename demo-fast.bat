@echo off
setlocal
call "%~dp0demo.bat" --no-tool %*
set "demo_exit=%errorlevel%"
if "%~1"=="" pause
exit /b %demo_exit%
