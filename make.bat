@echo off
if "%1"=="test" python scripts\run_tests.py
if "%1"=="eval" python scripts\argus.py eval
if "%1"=="run" python scripts\argus.py run --company "%COMPANY%"
