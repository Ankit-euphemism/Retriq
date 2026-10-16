@echo off

echo Starting Retriq project...

cd /d "%~dp0backend"
call .venv\Scripts\activate.bat
start "Retriq Backend" cmd /k "python -m main"

cd /d "%~dp0frontend"
start "" index.html
echo Retriq project is running. Press any key to exit.